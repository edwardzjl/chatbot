import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.chat_history import BaseChatMessageHistory

from chatbot.context import session_id
from chatbot.dependencies import MessageHistory, UserIdHeader
from chatbot.memory.history import ChatbotMessageHistory
from chatbot.models import Conversation as ORMConversation

router = APIRouter(
    prefix="/api/conversations/{conversation_id}/messages",
    tags=["messages"],
)


@router.put("/{message_idx}/thumbup")
async def thumbup(
    conversation_id: str,
    message_idx: int,
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    if not isinstance(history, ChatbotMessageHistory):
        # should never happen
        return
    session_id.set(f"{userid}:{conversation_id}")
    _msg: str = history.redis_client.lindex(history.key, message_idx)
    msg = json.loads(_msg.decode("utf-8"))
    msg["data"]["additional_kwargs"]["feedback"] = "thumbup"
    history.redis_client.lset(history.key, message_idx, json.dumps(msg))


@router.put("/{message_idx}/thumbdown")
async def thumbdown(
    conversation_id: str,
    message_idx: int,
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    if not isinstance(history, ChatbotMessageHistory):
        # should never happen
        return
    session_id.set(f"{userid}:{conversation_id}")
    _msg: str = history.redis_client.lindex(history.key, message_idx)
    msg = json.loads(_msg.decode("utf-8"))
    msg["data"]["additional_kwargs"]["feedback"] = "thumbdown"
    history.redis_client.lset(history.key, message_idx, json.dumps(msg))
