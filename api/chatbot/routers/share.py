from urllib.parse import urljoin
from uuid import uuid4
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import BaseMessage
from langgraph.graph.graph import CompiledGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from chatbot.dependencies import UserIdHeader, get_agent, get_sqlalchemy_session
from chatbot.models import Conversation as ORMConv, Share as ORMShare
from chatbot.schemas import ChatMessage, CreateShare, Share


# jlzhou: The resource name ("shares") is recommended by gemini, don't blame me.
router = APIRouter(
    prefix="/api/shares",
    tags=["share"],
)


@router.get("")
async def get_shares(
    session: AsyncSession = Depends(get_sqlalchemy_session),
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> list[Share]:
    """Get shares by userid"""
    # TODO: support pagination
    stmt = (
        select(ORMShare)
        .where(ORMShare.owner == userid)
        .order_by(ORMShare.created_at.desc())
    )
    return (await session.scalars(stmt)).all()


@router.get("/{share_id}")
async def get_share(
    share_id: str,
    session: AsyncSession = Depends(get_sqlalchemy_session),
    agent: CompiledGraph = Depends(get_agent),
) -> Share:
    """Get a share by id"""
    share: ORMShare = await session.get(ORMShare, share_id)

    config = {"configurable": share.snapshot_ref}
    state = await agent.aget_state(config)
    lc_msgs: list[BaseMessage] = state.values.get("messages", [])
    messages = [
        (
            ChatMessage.from_lc(lc_message=message, conv_id=share_id, from_=share.owner)
            if message.type == "human"
            else ChatMessage.from_lc(lc_message=message, conv_id=share_id)
        )
        for message in lc_msgs
    ]

    res = Share.model_validate(share)
    res.messages = messages
    return res


@router.post("", status_code=201)
async def create_share(
    payload: CreateShare,
    request: Request,
    userid: Annotated[str | None, UserIdHeader()] = None,
    session: AsyncSession = Depends(get_sqlalchemy_session),
    agent: CompiledGraph = Depends(get_agent),
) -> Share:
    # TODO: maybe only get the conv.owner
    conv: ORMConv = await session.get(ORMConv, payload.source_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config = {"configurable": {"thread_id": payload.source_id}}
    state = await agent.aget_state(config)
    snapshot_ref = state.config["configurable"]

    share_id = uuid4()
    shared_url = urljoin(str(request.url), f"/share/{share_id}")

    share = ORMShare(
        id=share_id,
        title=payload.title,
        owner=userid,
        url=shared_url,
        snapshot_ref=snapshot_ref,
    )
    session.add(share)
    await session.commit()
    return share


@router.delete("/{share_id}", status_code=204)
async def delete_share(
    share_id: str,
    session: AsyncSession = Depends(get_sqlalchemy_session),
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    # TODO: maybe only get the share.owner
    share: ORMShare = await session.get(ORMShare, share_id)
    if share.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    await session.delete(share)
    await session.commit()


@router.post("/{share_id}/forks", status_code=201)
async def fork_share(
    share_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> Any:
    # TODO: implementation
    ...
