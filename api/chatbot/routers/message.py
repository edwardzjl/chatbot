from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, HTTPException

from chatbot.dependencies import (
    AgentForStateDep,
    SqlalchemyROSessionDep,
    UserIdHeaderDep,
)
from chatbot.models import Conversation as ORMConversation

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

router = APIRouter(
    prefix="/api/conversations/{conversation_id}/messages",
    tags=["messages"],
)


# TODO: merge thumbup and thumbdown into one endpoint called feedback?
@router.put("/{message_id}/thumbup")
async def thumbup(
    conversation_id: UUID,
    message_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent: AgentForStateDep,
) -> None:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config = {"configurable": {"thread_id": conversation_id}}
    state = await agent.aget_state(config)

    # There should be only one message with the given id
    messages: list[BaseMessage] = [
        message for message in state.values["messages"] if message.id == message_id
    ]
    for message in messages:
        message.additional_kwargs["feedback"] = "thumbup"

    await agent.aupdate_state(
        config,
        {"messages": messages},
    )


@router.put("/{message_id}/thumbdown")
async def thumbdown(
    conversation_id: UUID,
    message_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent: AgentForStateDep,
) -> None:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if not conv:
        raise HTTPException(
            status_code=404, detail=f"Conversation {conversation_id} not found"
        )
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config = {"configurable": {"thread_id": conversation_id}}
    state = await agent.aget_state(config)

    # There should be only one message with the given id
    messages: list[BaseMessage] = [
        message for message in state.values["messages"] if message.id == message_id
    ]
    for message in messages:
        message.additional_kwargs["feedback"] = "thumbdown"

    await agent.aupdate_state(
        config,
        {"messages": messages},
    )
