import json
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain.chains.base import Chain
from langchain_core.chat_history import BaseChatMessageHistory
from loguru import logger

from chatbot.callbacks import (
    StreamingLLMCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.context import session_id
from chatbot.dependencies import UserIdHeader, get_conv_chain, get_message_history
from chatbot.history import ContextAwareMessageHistory
from chatbot.models import Conversation as ORMConversation
from chatbot.prompts import INSTRUCTION
from chatbot.schemas import (
    ChatMessage,
    Conversation,
    ConversationDetail,
    UpdateConversation,
)

router = APIRouter(
    prefix="/api",
    tags=["conversation"],
)


@router.get("/conversations")
async def get_conversations(
    userid: Annotated[str | None, UserIdHeader()] = None
) -> list[Conversation]:
    convs = await ORMConversation.find(ORMConversation.owner == userid).all()
    convs.sort(key=lambda x: x.updated_at, reverse=True)
    return [Conversation(**conv.dict()) for conv in convs]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    history: Annotated[BaseChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> ConversationDetail:
    conv = await ORMConversation.get(conversation_id)
    session_id.set(f"{userid}:{conversation_id}")
    return ConversationDetail(
        messages=[
            ChatMessage.from_lc(lc_message=message, conv_id=conversation_id, from_="ai")
            if message.type == "ai"
            else ChatMessage.from_lc(
                lc_message=message, conv_id=conversation_id, from_=userid
            )
            for message in history.messages
        ],
        **conv.dict(),
    )


@router.post("/conversations", status_code=201)
async def create_conversation(
    userid: Annotated[str | None, UserIdHeader()] = None
) -> ConversationDetail:
    conv = ORMConversation(title=f"New chat", owner=userid)
    await conv.save()
    return ConversationDetail(**conv.dict())


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    conv = await ORMConversation.get(conversation_id)
    conv.title = payload.title
    await conv.save()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    await ORMConversation.delete(conversation_id)


@router.websocket("/chat")
async def generate(
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


@router.put("/conversations/{conversation_id}/messages/{message_idx}/thumbup")
async def thumbup(
    conversation_id: str,
    message_idx: int,
    history: Annotated[BaseChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    if not isinstance(history, ContextAwareMessageHistory):
        # should never happen
        return
    session_id.set(f"{userid}:{conversation_id}")
    # redis pushes from left to right, so the first message is at index llen - 1
    # I have to get the message reversed.
    msg_count = history.redis_client.llen(history.key)
    lidx = msg_count - message_idx - 1
    _msg: str = history.redis_client.lindex(history.key, lidx)
    msg = json.loads(_msg.decode("utf-8"))
    msg["data"]["additional_kwargs"]["feedback"] = "thumbup"
    history.redis_client.lset(history.key, lidx, json.dumps(msg))


@router.put("/conversations/{conversation_id}/messages/{message_idx}/thumbdown")
async def thumbdown(
    conversation_id: str,
    message_idx: int,
    history: Annotated[BaseChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    if not isinstance(history, ContextAwareMessageHistory):
        # should never happen
        return
    session_id.set(f"{userid}:{conversation_id}")
    msg = history.get_message(message_idx)
    # redis pushes from left to right, so the first message is at index llen - 1
    # I have to get the message reversed.
    msg_count = history.redis_client.llen(history.key)
    lidx = msg_count - message_idx - 1
    _msg: str = history.redis_client.lindex(history.key, lidx)
    msg = json.loads(_msg.decode("utf-8"))
    msg["data"]["additional_kwargs"]["feedback"] = "thumbdown"
    history.redis_client.lset(history.key, lidx, json.dumps(msg))
