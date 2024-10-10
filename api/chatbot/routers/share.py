from urllib.parse import urljoin
from uuid import uuid4
from typing import Any

from fastapi import APIRouter, HTTPException
from langchain_core.messages import BaseMessage
from sqlalchemy import select
from starlette.requests import Request

from chatbot.dependencies import AgentStateDep, SqlalchemySessionDep, UserIdHeaderDep
from chatbot.models import Conversation as ORMConv, Share as ORMShare
from chatbot.schemas import ChatMessage, CreateShare, Share


# jlzhou: The resource name ("shares") is recommended by gemini, don't blame me.
router = APIRouter(
    prefix="/api/shares",
    tags=["share"],
)


@router.get("")
async def get_shares(
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
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
    session: SqlalchemySessionDep,
    agent_state: AgentStateDep,
) -> Share:
    """Get a share by id"""
    share: ORMShare = await session.get(ORMShare, share_id)

    lc_msgs: list[BaseMessage] = agent_state.values.get("messages", [])
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
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
    agent_state: AgentStateDep,
) -> Share:
    # TODO: maybe only get the conv.owner
    conv: ORMConv = await session.get(ORMConv, payload.source_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    snapshot_ref = agent_state.config["configurable"]

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
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
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
    userid: UserIdHeaderDep,
) -> Any:
    # TODO: implementation
    ...
