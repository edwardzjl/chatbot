from datetime import date
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from loguru import logger

from chatbot.chains.conversation import conv_chain
from chatbot.chains.summarization import smry_chain
from chatbot.context import session_id
from chatbot.dependencies import UserIdHeader
from chatbot.memory import history
from chatbot.models import Conversation
from chatbot.schemas import AIChatMessage, ChatMessage, InfoMessage
from chatbot.utils import utcnow

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await websocket.accept()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            message = ChatMessage.model_validate_json(payload)
            conv = await Conversation.get(message.conversation)
            if conv.owner != userid:
                # TODO: I'm not sure whether this is the correct way to handle this.
                # See websocket code definitions here: <https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code>
                raise WebSocketException(code=3403, reason="authorization error")
            # set session_id early to ensure history is loaded correctly.
            session_id.set(f"{userid}:{message.conversation}")
            chain_metadata = {
                "conversation_id": message.conversation,
                "userid": userid,
            }
            async for event in conv_chain.astream_events(
                input={
                    "input": message.content,
                    # create a new date on every message to solve message across days.
                    "date": date.today(),
                },
                config={
                    "run_name": "chat",
                    "metadata": chain_metadata,
                },
                version="v1",
            ):
                logger.trace(f"event: {event}")
                match event["event"]:
                    case "on_chain_end":
                        if event["name"] == "chat":
                            msg = AIChatMessage(
                                parent_id=message.id,
                                id=event["run_id"],
                                conversation=message.conversation,
                                content=event["data"]["output"],
                            )
                            await history.aadd_messages([message.to_lc(), msg.to_lc()])
                    case "on_chat_model_start":
                        logger.debug(f"event: {event}")
                        msg = AIChatMessage(
                            parent_id=message.id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            content=None,
                            type="stream/start",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_chat_model_stream":
                        msg = ChatMessage(
                            parent_id=message.id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            from_="ai",
                            content=event["data"]["chunk"].content,
                            type="stream/text",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_chat_model_end":
                        logger.debug(f"event: {event}")
                        msg = AIChatMessage(
                            parent_id=message.id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            content=None,
                            type="stream/end",
                        )
                        await websocket.send_text(msg.model_dump_json())
            conv.last_message_at = utcnow()
            await conv.save()
            # summarize if required
            if message.additional_kwargs and message.additional_kwargs.get(
                "require_summarization", False
            ):
                title_raw: str = await smry_chain.ainvoke(
                    input={},
                    config={"metadata": chain_metadata},
                )
                title = title_raw.strip('"')
                conv.title = title
                await conv.save()
                info_message = InfoMessage(
                    conversation=message.conversation,
                    from_="ai",
                    content={
                        "type": "title-generated",
                        "payload": title,
                    },
                )
                await websocket.send_text(info_message.model_dump_json())
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            return
        except Exception as e:
            logger.exception(f"Something goes wrong: {e}")
