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
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from loguru import logger

from chatbot.context import session_id
from chatbot.dependencies import ChatMemory, ConvChain, Llm, UserIdHeader
from chatbot.models import Conversation
from chatbot.schemas import ChatMessage, InfoMessage
from chatbot.summarization import summarize
from chatbot.utils import utcnow

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    conv_chain: Annotated[Chain, Depends(ConvChain)],
    llm: Annotated[BaseLLM, Depends(Llm)],
    memory: Annotated[BaseMemory, Depends(ChatMemory)],
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
            async for event in conv_chain.astream_events(
                input={
                    "input": message.content,
                    # create a new date on every message to solve message across days.
                    "date": date.today(),
                },
                include_run_info=True,
                version="v1",
            ):
                logger.trace(f"event: {event}")
                kind = event["event"]
                parent_run_id = None
                match kind:
                    case "on_chain_start":
                        # TODO: maybe it's a little hacky
                        parent_run_id = event["run_id"]
                    case "on_llm_start":
                        msg = ChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            from_="ai",
                            content=None,
                            type="stream/start",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_llm_stream":
                        msg = ChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            from_="ai",
                            content=event["data"]["chunk"],
                            type="stream/text",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_llm_end":
                        msg = ChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            from_="ai",
                            content=None,
                            type="stream/end",
                        )
                        await websocket.send_text(msg.model_dump_json())
                    case "on_llm_error":
                        msg = ChatMessage(
                            parent_id=parent_run_id,
                            id=event["run_id"],
                            conversation=message.conversation,
                            from_="ai",
                            content=f"llm error: {event['data']}",
                            type="error",
                        )
                        await websocket.send_text(msg.model_dump_json())
            conv.updated_at = utcnow()
            await conv.save()
            # summarize if required
            if (
                message.additional_kwargs
                and "require_summarization" in message.additional_kwargs
                and message.additional_kwargs["require_summarization"]
            ):
                title = await summarize(llm, memory)
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
            logger.error(f"Something goes wrong, err: {e}")
