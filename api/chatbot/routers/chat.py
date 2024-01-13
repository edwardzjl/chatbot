from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain.chains.base import Chain
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from loguru import logger

from chatbot.callbacks import (
    StreamingLLMCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.context import session_id
from chatbot.dependencies import ChatMemory, ConvChain, Llm, UserIdHeader
from chatbot.schemas import ChatMessage, InfoMessage
from chatbot.summarization import summarize

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
            session_id.set(f"{userid}:{message.conversation}")
            streaming_callback = StreamingLLMCallbackHandler(
                websocket, message.conversation
            )
            update_conversation_callback = UpdateConversationCallbackHandler(
                message.conversation
            )
            # create a new date on every message to solve message across days.
            await conv_chain.arun(
                date=date.today(),
                input=message.content,
                callbacks=[streaming_callback, update_conversation_callback],
            )
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
