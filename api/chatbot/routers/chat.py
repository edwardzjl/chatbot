import logging
from functools import partial
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Request,
)
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.ai import UsageMetadata
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from openai import RateLimitError
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from chatbot.dependencies import UserIdHeaderDep
from chatbot.dependencies.agent import AgentWrapperDep, SmrChainWrapperDep
from chatbot.dependencies.db import SqlalchemySessionMakerDep
from chatbot.metrics.llm import input_tokens, output_tokens
from chatbot.models import Conversation
from chatbot.schemas import (
    ChatMessage,
    ErrorMessage,
    InfoMessage,
    HumanChatMessage,
)
from chatbot.utils import utcnow


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat")


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request, considering proxy headers."""
    # Check X-Forwarded-For header (common when behind reverse proxy/load balancer)
    if forwarded_for := request.headers.get("x-forwarded-for"):
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header (common with nginx)
    if real_ip := request.headers.get("x-real-ip"):
        return real_ip.strip()

    # Fall back to direct connection IP
    if request.client and request.client.host:
        return request.client.host

    # Final fallback
    return "unknown"


@router.post("/stream")
async def chat_stream(
    message: HumanChatMessage,
    request: Request,
    userid: UserIdHeaderDep,
    agent_wrapper: AgentWrapperDep,
    smry_chain_wrapper: SmrChainWrapperDep,
    session_maker: SqlalchemySessionMakerDep,
    background_tasks: BackgroundTasks,
):
    """HTTP streaming endpoint for chat interactions using Server-Sent Events."""

    await validate_conversation_owner(session_maker, message.conversation, userid)
    selected_model = message.additional_kwargs.get("model_name")
    runnable_config: RunnableConfig = {
        "run_name": "chat",
        "metadata": {
            "conversation_id": message.conversation,
            "userid": userid,
            "client_ip": get_client_ip(request),
        },
        "configurable": {"thread_id": message.conversation},
    }

    async def generate_stream():
        try:
            async with agent_wrapper(selected_model) as agent:
                async for msg, metadata in agent.astream(
                    input={"messages": [message.to_lc()]},
                    config=runnable_config,
                    stream_mode="messages",
                    durability="async",
                ):
                    if "internal" in metadata.get("tags", []):
                        continue  # Skip internal messages.

                    _msg = ChatMessage.from_lc(
                        msg,
                        parent_id=message.id,
                        conversation=message.conversation,
                    )

                    # Send as Server-Sent Event
                    sse_data = f"data: {_msg.model_dump_json()}\n\n"
                    yield sse_data

                    if (
                        isinstance(msg, AIMessage)
                        and (usage_metadata := msg.usage_metadata) is not None
                    ):
                        update_usage_metrics(
                            userid,
                            msg.response_metadata,
                            usage_metadata,
                        )

                background_tasks.add_task(
                    update_conv,
                    session_maker,
                    message.conversation,
                    last_message_at=utcnow(),
                )

                # summarize if required
                if message.additional_kwargs and message.additional_kwargs.get(
                    "require_summarization", False
                ):
                    title = await generate_conversation_title(
                        agent=agent,
                        smry_chain_wrapper=smry_chain_wrapper,
                        selected_model=selected_model,
                        runnable_config=runnable_config,
                    )
                    if title:
                        background_tasks.add_task(
                            update_conv,
                            session_maker,
                            message.conversation,
                            title=title,
                        )

                        info_message = InfoMessage(
                            conversation=message.conversation,
                            content={
                                "type": "title-generated",
                                "payload": title,
                            },
                        )
                        # Send title update as SSE
                        sse_data = f"data: {info_message.model_dump_json()}\n\n"
                        yield sse_data

        except RateLimitError:
            err_message = ErrorMessage(
                content="Rate limit exceeded. Please try again later.",
            )
            sse_data = f"data: {err_message.model_dump_json()}\n\n"
            yield sse_data
        except Exception as e:  # noqa: BLE001
            logger.exception("Something goes wrong: %s", e)
            err_message = ErrorMessage(
                content="An error occurred while processing your request.",
            )
            sse_data = f"data: {err_message.model_dump_json()}\n\n"
            yield sse_data

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for real-time streaming
        },
    )


async def validate_conversation_owner(
    session_maker: async_sessionmaker[AsyncSession],
    conversation_id: UUID | str,
    userid: str,
) -> Conversation:
    """Validate that the user owns the conversation."""
    if not isinstance(conversation_id, UUID):
        conversation_id = UUID(conversation_id)
    async with session_maker() as session:
        conv: Conversation = await session.get(Conversation, conversation_id)
    if conv.owner != userid:
        raise HTTPException(status_code=403, detail="authorization error")
    return conv


async def generate_conversation_title(
    agent: CompiledStateGraph,
    smry_chain_wrapper: partial[Runnable],
    selected_model: str,
    runnable_config: RunnableConfig,
):
    """Generate a title for the conversation."""
    state = await agent.aget_state(runnable_config)
    msgs: list[BaseMessage] = state.values.get("messages", [])

    smry_chain = smry_chain_wrapper(selected_model)
    title_raw: str = await smry_chain.ainvoke(
        input={"messages": msgs},
        config=runnable_config,
    )
    return title_raw.strip('"')


def update_usage_metrics(
    userid: str, response_metadata: dict, usage_metadata: UsageMetadata | None = None
) -> None:
    if (model_name := response_metadata.get("model_name")) is None:
        return

    if usage_metadata is None:
        return

    input_tokens.labels(
        user_id=userid,
        model_name=model_name,
    ).inc(usage_metadata["input_tokens"])
    output_tokens.labels(
        user_id=userid,
        model_name=model_name,
    ).inc(usage_metadata["output_tokens"])


async def update_conv(
    session_maker: async_sessionmaker[AsyncSession],
    conv_id: UUID,
    **fields: Any,
) -> None:
    """Update arbitrary fields of a conversation."""
    if not fields:
        return  # nothing to update

    async with session_maker() as session:
        await session.execute(
            update(Conversation).where(Conversation.id == conv_id).values(**fields)
        )
        await session.commit()
