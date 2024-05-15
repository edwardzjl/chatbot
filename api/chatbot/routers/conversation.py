from typing import Annotated

from fastapi import APIRouter, HTTPException

from chatbot.chains.summarization import smry_chain
from chatbot.context import session_id
from chatbot.dependencies import UserIdHeader
from chatbot.memory import history
from chatbot.models import Conversation as ORMConversation
from chatbot.schemas import (
    ChatMessage,
    Conversation,
    ConversationDetail,
    CreateConversation,
    UpdateConversation,
)

router = APIRouter(
    prefix="/api/conversations",
    tags=["conversation"],
)


@router.get("")
async def get_conversations(
    userid: Annotated[str | None, UserIdHeader()] = None
) -> list[Conversation]:
    convs = await ORMConversation.find(ORMConversation.owner == userid).all()
    convs.sort(key=lambda x: (x.pinned, x.last_message_at), reverse=True)
    return [Conversation(**conv.model_dump()) for conv in convs]


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> ConversationDetail:
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    session_id.set(f"{userid}:{conversation_id}")
    msgs = await history.aget_messages()
    return ConversationDetail(
        messages=[
            (
                ChatMessage.from_lc(
                    lc_message=message, conv_id=conversation_id, from_="ai"
                )
                if message.type == "ai"
                else ChatMessage.from_lc(
                    lc_message=message, conv_id=conversation_id, from_=userid
                )
            )
            for message in msgs
        ],
        **conv.model_dump(),
    )


@router.post("", status_code=201)
async def create_conversation(
    payload: CreateConversation, userid: Annotated[str | None, UserIdHeader()] = None
) -> ConversationDetail:
    conv = ORMConversation(title=payload.title, owner=userid)
    await conv.save()
    return ConversationDetail(**conv.model_dump())


@router.put("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> ConversationDetail:
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    modified = False
    if payload.title is not None:
        conv.title = payload.title
        modified = True
    if payload.pinned is not None:
        conv.pinned = payload.pinned
        modified = True
    if modified:
        await conv.save()
    return ConversationDetail(**conv.model_dump())


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    await ORMConversation.delete(conversation_id)


@router.post("/{conversation_id}/summarization", status_code=201)
async def summarize(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> dict[str, str]:
    conv = await ORMConversation.get(conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    session_id.set(f"{userid}:{conversation_id}")

    title_raw: str = await smry_chain.ainvoke(
        input={},
        config={
            "metadata": {
                "conversation_id": conversation_id,
                "userid": userid,
            }
        },
    )
    title = title_raw.strip('"')
    conv.title = title
    await conv.save()
    return {"title": title}
