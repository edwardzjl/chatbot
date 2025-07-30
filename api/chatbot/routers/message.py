from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException
from langchain_core.runnables import RunnableConfig

from chatbot.dependencies import (
    AgentForStateDep,
    SqlalchemyROSessionDep,
    UserIdHeaderDep,
    uuid_or_404,
)
from chatbot.models import Conversation as ORMConversation

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["messages"],
)


# TODO: merge thumbup and thumbdown into one endpoint called feedback?
@router.put("/{message_id}/thumbup")
async def thumbup(
    conversation_id: Annotated[UUID, uuid_or_404("conversation_id", "Conversation")],
    message_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent: AgentForStateDep,
) -> None:
    conv: ORMConversation = await session.get_one(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config: RunnableConfig = {"configurable": {"thread_id": conversation_id}}
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
    conversation_id: Annotated[UUID, uuid_or_404("conversation_id", "Conversation")],
    message_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent: AgentForStateDep,
) -> None:
    conv: ORMConversation = await session.get_one(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config: RunnableConfig = {"configurable": {"thread_id": conversation_id}}
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
