from urllib.parse import urljoin
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException
from langchain_core.messages import BaseMessage
from starlette.requests import Request

from chatbot.dependencies import UserIdHeader
from chatbot.models import Conversation as ORMConv, Share as ORMShare
from chatbot.schemas import ChatMessage, CreateShare, Share
from chatbot.state import app_state


# jlzhou: The resource name ("shares") is recommended by gemini, don't blame me.
router = APIRouter(
    prefix="/api/shares",
    tags=["share"],
)


@router.get("")
async def get_shares(
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> list[Share]:
    """Get shares by userid"""
    shares = await ORMShare.find(ORMShare.owner == userid).all()
    shares.sort(key=lambda x: (x.created_at), reverse=True)
    return [Share(**share.model_dump()) for share in shares]


@router.get("/{share_id}")
async def get_share(share_id: str) -> Share:
    """Get a share by id"""
    share = await ORMShare.get(share_id)
    config = {"configurable": share.snapshot_ref}
    state = await app_state.agent.aget_state(config)
    msgs: list[BaseMessage] = state.values.get("messages", [])

    return Share(
        messages=[
            (
                ChatMessage.from_lc(
                    lc_message=message, conv_id=share_id, from_=share.owner
                )
                if message.type == "human"
                else ChatMessage.from_lc(lc_message=message, conv_id=share_id)
            )
            for message in msgs
        ],
        **share.model_dump(),
    )


@router.post("", status_code=201)
async def create_share(
    payload: CreateShare,
    request: Request,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> Share:
    conv = await ORMConv.get(payload.source_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    config = {"configurable": {"thread_id": payload.source_id}}
    state = await app_state.agent.aget_state(config)
    snapshot_ref = state.config["configurable"]
    share = ORMShare(
        title=payload.title,
        owner=userid,
        url="",
        source_id=payload.source_id,
        snapshot_ref=snapshot_ref,
    )
    shared_url = urljoin(str(request.url), f"/share/{share.pk}")
    share.url = shared_url
    await share.save()
    return Share(**share.model_dump())


@router.delete("/{share_id}", status_code=204)
async def delete_share(
    share_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    share = await ORMConv.get(share_id)
    if share.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    await ORMConv.delete(share_id)


@router.post("/{share_id}/forks", status_code=201)
async def fork_share(
    share_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> Any:
    # TODO: implementation
    ...
