from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urljoin
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from fastapi_pagination.cursor import CursorPage
from fastapi_pagination.ext.sqlalchemy import paginate
from langchain_core.runnables import RunnableConfig
from sqlalchemy import select
from starlette.requests import Request

from chatbot.dependencies import (
    AgentForStateDep,
    SqlalchemyROSessionDep,
    SqlalchemySessionDep,
    UserIdHeaderDep,
    uuid_or_404,
)
from chatbot.models import Conversation as ORMConv
from chatbot.models import Share as ORMShare
from chatbot.schemas import ChatMessage, CreateShare, Share

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

# jlzhou: The resource name ("shares") is recommended by gemini, don't blame me.
router = APIRouter(prefix="/shares")


@router.get("")
async def get_shares(
    userid: UserIdHeaderDep,
    session: SqlalchemyROSessionDep,
) -> CursorPage[Share]:
    """Get shares by userid"""
    stmt = (
        select(ORMShare)
        .where(ORMShare.owner == userid)
        .order_by(ORMShare.created_at.desc())
    )
    page = await paginate(session, stmt)
    return page


@router.get("/{share_id}")
async def get_share(
    share_id: Annotated[UUID, uuid_or_404("share_id", "Share")],
    session: SqlalchemyROSessionDep,
    agent: AgentForStateDep,
) -> Share:
    """Get a share by id"""
    share: ORMShare = await session.get_one(ORMShare, share_id)
    res = Share.model_validate(share)

    config: RunnableConfig = {"configurable": share.snapshot_ref}
    agent_state = await agent.aget_state(config)
    lc_msgs: list[BaseMessage] = agent_state.values.get("messages", [])
    messages = [ChatMessage.from_lc(message) for message in lc_msgs]
    res.messages = messages
    return res


@router.post("", status_code=201)
async def create_share(
    payload: CreateShare,
    request: Request,
    userid: UserIdHeaderDep,
    session: SqlalchemySessionDep,
    agent: AgentForStateDep,
) -> Share:
    # TODO: maybe only get the conv.owner
    conv: ORMConv = await session.get_one(ORMConv, payload.source_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")

    config: RunnableConfig = {"configurable": {"thread_id": payload.source_id}}
    agent_state = await agent.aget_state(config)
    snapshot_ref = agent_state.config["configurable"]

    share_id = uuid4()
    shared_url = urljoin(str(request.base_url), f"/share/{share_id}")

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
    if not share:
        return
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
