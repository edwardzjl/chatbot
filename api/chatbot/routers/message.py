from typing import Annotated

from fastapi import APIRouter, HTTPException
from langchain_core.messages import BaseMessage

from chatbot.dependencies import UserIdHeader
from chatbot.models import Conversation as ORMConversation
from chatbot.state import app_state

router = APIRouter(
    prefix="/api/conversations/{conversation_id}/messages",
    tags=["messages"],
)


# TODO: merge thumbup and thumbdown into one endpoint called feedback?
@router.put("/{message_id}/thumbup")
async def thumbup(
    conversation_id: str,
    message_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config = {"configurable": {"thread_id": conversation_id}}
    state = await app_state.agent.aget_state(config)

    # There should be only one message with the given id
    messages: list[BaseMessage] = [
        message for message in state.values["messages"] if message.id == message_id
    ]
    for message in messages:
        message.additional_kwargs["feedback"] = "thumbup"
    # TODO: IDK why but partial updating works
    # See <https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/#branch-off-a-past-state>
    await app_state.agent.aupdate_state(
        config,
        {"messages": messages},
    )


@router.put("/{message_id}/thumbdown")
async def thumbdown(
    conversation_id: str,
    message_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    """Using message index as the uuid is in the message body which is json dumped into redis,
    and is impossible to filter on.
    Also separate thumbup and thumbdown into two endpoints to make it more RESTful."""
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config = {"configurable": {"thread_id": conversation_id}}
    state = await app_state.agent.aget_state(config)

    # There should be only one message with the given id
    messages: list[BaseMessage] = [
        message for message in state.values["messages"] if message.id == message_id
    ]
    for message in messages:
        message.additional_kwargs["feedback"] = "thumbdown"
    # TODO: IDK why but partial updating works
    # See <https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/#branch-off-a-past-state>
    await app_state.agent.aupdate_state(
        config,
        {"messages": messages},
    )
