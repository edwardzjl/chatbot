import json
from typing import Annotated

from fastapi import APIRouter, Depends
from langchain_core.chat_history import BaseChatMessageHistory

from chatbot.context import session_id
from chatbot.dependencies import MessageHistory, UserIdHeader
from chatbot.history import ContextAwareMessageHistory

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
