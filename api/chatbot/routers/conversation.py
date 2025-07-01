from fastapi import APIRouter, HTTPException
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from langchain_core.messages import BaseMessage, trim_messages
from sqlalchemy import select
from uuid import UUID

from chatbot.dependencies import (
    AgentStateDep,
    SmrChainDep,
    SqlalchemyROSessionDep,
    SqlalchemySessionDep,
    UserIdHeaderDep,
)
from chatbot.models import Conversation as ORMConversation
from chatbot.schemas import (
    ChatMessage,
    Conversation,
    ConversationDetail,
    CreateConversation,
    UpdateConversation,
)

router = APIRouter(
    prefix="/conversations",
    tags=["conversation"],
)


@router.get("")
async def get_conversations(
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
) -> CursorPage[Conversation]:
    stmt = (
        select(ORMConversation)
        .where(ORMConversation.owner == userid)
        .order_by(ORMConversation.pinned.desc(), ORMConversation.last_message_at.desc())
    )
    page = await paginate(session, stmt)
    return page


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent_state: AgentStateDep,
) -> ConversationDetail:
    conv: ORMConversation = await session.get_one(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    res = ConversationDetail.model_validate(conv)

    lc_msgs: list[BaseMessage] = agent_state.values.get("messages", [])
    messages = [ChatMessage.from_lc(message) for message in lc_msgs]
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
    conversation_id: UUID,
    payload: UpdateConversation,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> ConversationDetail:
    conv: ORMConversation = await session.get_one(ORMConversation, conversation_id)
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
    conversation_id: UUID,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
) -> None:
    conv: ORMConversation = await session.get(ORMConversation, conversation_id)
    if not conv:
        return
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    await session.delete(conv)
    await session.commit()


@router.post("/{conversation_id}/summarization", status_code=201)
async def summarize(
    conversation_id: UUID,
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
    agent_state: AgentStateDep,
    smry_chain: SmrChainDep,
) -> dict[str, str]:
    conv: ORMConversation = await session.get_one(ORMConversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    msgs: list[BaseMessage] = agent_state.values.get("messages", [])

    windowed_messages = trim_messages(
        msgs,
        token_counter=len,
        max_tokens=20,
        start_on="human",  # This means that the first message should be from the user after trimming, which also means that we abandon the original system message.
    )

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
