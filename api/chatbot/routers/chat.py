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
from chatbot.dependencies import UserIdHeader, get_conv_chain
from chatbot.prompts import INSTRUCTION
from chatbot.schemas import ChatMessage

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    conv_chain: Annotated[Chain, Depends(get_conv_chain)],
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await websocket.accept()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            system_message = INSTRUCTION.format(date=date.today())
            message = ChatMessage.model_validate_json(payload)
            session_id.set(f"{userid}:{message.conversation}")
            streaming_callback = StreamingLLMCallbackHandler(
                websocket, message.conversation
            )
            update_conversation_callback = UpdateConversationCallbackHandler(
                message.conversation
            )
            await conv_chain.arun(
                system_message=system_message,
                input=message.content,
                callbacks=[streaming_callback, update_conversation_callback],
            )
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            return
        except Exception as e:
            logger.error(f"Something goes wrong, err: {e}")
