from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from langchain.chains.base import Chain
from langchain_core.chat_history import BaseChatMessageHistory
from loguru import logger

from chatbot.config import settings
from chatbot.context import session_id
from chatbot.dependencies import ConvChain, MessageHistory, SmryChain, UserIdHeader
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
    conv_chain: Annotated[Chain, Depends(ConvChain)],
    smry_chain: Annotated[Chain, Depends(SmryChain)],
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)],
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
            parent_run_id = None
            async for event in conv_chain.astream_events(
                input={
                    "input": message.content,
                    # create a new date on every message to solve message across days.
                    "date": date.today(),
                },
                include_run_info=True,
                version="v1",
                config={"metadata": chain_metadata},
            ):
                logger.trace(f"event: {event}")
                match event["event"]:
                    case "on_chain_start":
                        parent_run_id = event["run_id"]
                        history.add_message(message.to_lc())
                    case "on_chain_end":
                        msg = AIChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            # TODO: I think this can be improved on langchain side.
                            content=event["data"]["output"]["text"].removesuffix(
                                settings.llm.eos_token
                            ),
                        )
                        history.add_message(msg.to_lc())
                    case "on_chat_model_start":
                        logger.debug(f"event: {event}")
                        msg = AIChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            content=None,
                            type="stream/start",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_chat_model_stream":
                        # openai streaming provides eos token as last chunk, but langchain does not provide stop reason.
                        # It will be better if langchain could provide sth like event["data"]["chunk"].finish_reason == "eos_token"
                        if (
                            content := event["data"]["chunk"].content
                        ) != settings.llm.eos_token:
                            msg = ChatMessage(
                                parent_id=parent_run_id,
                                id=event["run_id"],
                                conversation=message.conversation,
                                from_="ai",
                                content=content,
                                type="stream/text",
                            )
                            await websocket.send_text(msg.model_dump_json())
                    case "on_chat_model_end":
                        logger.debug(f"event: {event}")
                        msg = AIChatMessage(
                            parent_id=parent_run_id,
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
                res = await smry_chain.ainvoke(
                    input={},
                    config={"metadata": chain_metadata},
                )
                title = res[smry_chain.output_key]
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
        except Exception:
            logger.exception("Something goes wrong")
