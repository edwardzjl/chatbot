from fastapi import APIRouter, HTTPException
from langchain_core.messages import BaseMessage, trim_messages
from sqlalchemy import select

from chatbot.chains.summarization import create_smry_chain
from chatbot.dependencies import AgentStateDep, SqlalchemySessionDep, UserIdHeaderDep
from chatbot.models import Conversation as ORMConversation
from chatbot.schemas import (
    ChatMessage,
    Conversation,
    ConversationDetail,
    CreateConversation,
    UpdateConversation,
)
from chatbot.state import chat_model

router = APIRouter(
    prefix="/api/conversations",
    tags=["conversation"],
)


@router.get("")
async def get_conversations(
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> list[Conversation]:
    # TODO: support pagination
    stmt = (
        select(ORMConversation)
        .where(ORMConversation.owner == userid)
        .order_by(ORMConversation.created_at.desc())
    )
    return (await session.scalars(stmt)).all()


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
    agent_state: AgentStateDep,
) -> ConversationDetail:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    lc_msgs: list[BaseMessage] = agent_state.values.get("messages", [])
    messages = [
        (
            ChatMessage.from_lc(
                lc_message=message, conv_id=conversation_id, from_=userid
            )
            if message.type == "human"
            else ChatMessage.from_lc(lc_message=message, conv_id=conversation_id)
        )
        for message in lc_msgs
    ]

    res = ConversationDetail.model_validate(conv)
    res.messages = messages
    return res


@router.post("", status_code=201)
async def create_conversation(
    payload: CreateConversation,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> ConversationDetail:
    conv = ORMConversation(title=payload.title, owner=userid)
    session.add(conv)
    await session.commit()
    return conv


@router.put("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> ConversationDetail:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    if payload.title is not None:
        conv.title = payload.title
    if payload.pinned is not None:
        conv.pinned = payload.pinned
    await session.commit()
    return conv


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> None:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    await session.delete(conv)
    await session.commit()


@router.post("/{conversation_id}/summarization", status_code=201)
async def summarize(
    conversation_id: str,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
    agent_state: AgentStateDep,
) -> dict[str, str]:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    msgs: list[BaseMessage] = agent_state.values.get("messages", [])

    windowed_messages = trim_messages(
        msgs,
        token_counter=len,
        max_tokens=20,
        start_on="human",  # This means that the first message should be from the user after trimming.
    )

    smry_chain = create_smry_chain(chat_model)
    title_raw: str = await smry_chain.ainvoke(
        input={"messages": windowed_messages},
        config={
            "metadata": {
                "conversation_id": conversation_id,
                "userid": userid,
            }
        },
    )
    title = title_raw.strip('"')
    conv.title = title
    await session.commit()
    return {"title": title}
