from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain.chains.base import Chain
from loguru import logger

from chatbot.callbacks import (
    StreamingLLMCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.context import session_id
from chatbot.dependencies import ConvChain, UserIdHeader
from chatbot.schemas import ChatMessage

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    conv_chain: Annotated[Chain, Depends(ConvChain)],
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
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            return
        except Exception as e:
            logger.error(f"Something goes wrong, err: {e}")
