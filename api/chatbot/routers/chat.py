import logging
from functools import partial
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from chatbot.dependencies import UserIdHeaderDep
from chatbot.dependencies.agent import AgentWrapperDep, SmrChainWrapperDep
from chatbot.dependencies.db import SqlalchemySessionMakerDep
from chatbot.metrics import connected_clients
from chatbot.metrics.llm import input_tokens, output_tokens
from chatbot.models import Conversation
from chatbot.schemas import (
    AIChatMessage,
    ChatMessage,
    InfoMessage,
    HumanChatMessage,
)
from chatbot.utils import utcnow


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    userid: UserIdHeaderDep,
    agent_wrapper: AgentWrapperDep,
    smry_chain_wrapper: SmrChainWrapperDep,
    session_maker: SqlalchemySessionMakerDep,
):
    await websocket.accept()
    connected_clients.inc()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            message = HumanChatMessage.model_validate_json(payload)

            conv = await validate_conversation_owner(
                session_maker, message.conversation, userid
            )

            selected_model = message.additional_kwargs.get("model_name")

            chain_metadata = {
                "conversation_id": message.conversation,
                "userid": userid,
                "client_ip": websocket.client.host,
            }

            runtime_configuration = {"thread_id": message.conversation}

            async with agent_wrapper(selected_model) as agent:
                async for event in agent.astream_events(
                    input={"messages": [message.to_lc()]},
                    config={
                        "run_name": "chat",
                        "metadata": chain_metadata,
                        "configurable": runtime_configuration,
                    },
                    version="v2",
                ):
                    event_name: str = event["name"]
                    if event_name.startswith("_") or event_name.startswith(
                        "ChannelWrite"
                    ):
                        # events starts with "_" or "ChannelWrite" are langchain's internal events,
                        # for example '_Exception' and 'ChannelWrite<agent,file,agent_outcome,intermediate_steps>'
                        # skip for mainly 2 reasons:
                        # 1. we don't want to expose internal event to the user (websocket or history)
                        # 2. we want to keep the conversation history as short as possible
                        continue

                    tags: list[str] = event["tags"]
                    if "internal" in tags:
                        # Our internal events are not supposed to be exposed to the user.
                        continue

                    logger.debug("event: %s", event)
                    evt: str = event["event"]
                    if evt == "on_chat_model_start":
                        # Send an empty non-chunk message to start the streaming.
                        msg = AIChatMessage(
                            parent_id=message.id,
                            id=f"run--{event['run_id']}",
                            conversation=message.conversation,
                            content="",  # Tired of handling null / undefined in js, simply sending an empty string.
                        )
                        await websocket.send_text(msg.model_dump_json())
                    if evt == "on_chat_model_stream":
                        msg = ChatMessage.from_lc(
                            event["data"]["chunk"],
                            parent_id=message.id,
                            conversation=message.conversation,
                        )
                        await websocket.send_text(msg.model_dump_json())
                    if evt == "on_chat_model_end":
                        msg: AIMessage = event["data"]["output"]
                        if (usage_metadata := msg.usage_metadata) is not None:
                            model_name = msg.response_metadata.get("model_name")
                            input_tokens.labels(
                                user_id=userid,
                                model_name=model_name,
                            ).inc(usage_metadata["input_tokens"])
                            output_tokens.labels(
                                user_id=userid,
                                model_name=model_name,
                            ).inc(usage_metadata["output_tokens"])

                conv = await update_conversation_last_message_at(session_maker, conv)

                # summarize if required
                if message.additional_kwargs and message.additional_kwargs.get(
                    "require_summarization", False
                ):
                    title = await generate_conversation_title(
                        agent=agent,
                        smry_chain_wrapper=smry_chain_wrapper,
                        conversation_id=message.conversation,
                        selected_model=selected_model,
                        chain_metadata=chain_metadata,
                    )
                    if title:
                        conv.title = title
                        async with session_maker() as session:
                            conv = await session.merge(conv)
                            await session.commit()

                        info_message = InfoMessage(
                            conversation=message.conversation,
                            content={
                                "type": "title-generated",
                                "payload": title,
                            },
                        )
                        await websocket.send_text(info_message.model_dump_json())
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            connected_clients.dec()
            return
        except Exception as e:  # noqa: BLE001
            logger.exception("Something goes wrong: %s", e)


async def validate_conversation_owner(
    session_maker: async_sessionmaker[AsyncSession],
    conversation_id: UUID | str,
    userid: str,
) -> Conversation:
    """Validate that the user owns the conversation."""
    if not isinstance(conversation_id, UUID):
        # In most cases, I don't need to do anything. SQLAlchemy will do the conversion for me.
        # However, SQLite doesn't have a native UUID type.
        # See <https://github.com/sqlalchemy/sqlalchemy/discussions/9290#discussioncomment-4953349>
        conversation_id = UUID(conversation_id)
    async with session_maker() as session:
        conv: Conversation = await session.get(Conversation, conversation_id)
    if conv.owner != userid:
        raise WebSocketException(code=3403, reason="authorization error")
    return conv


async def update_conversation_last_message_at(
    session_maker: async_sessionmaker[AsyncSession], conv: Conversation
):
    """Update the conversation's last_message_at timestamp."""
    conv.last_message_at = utcnow()
    async with session_maker() as session:
        conv = await session.merge(conv)
        await session.commit()
    return conv


async def generate_conversation_title(
    agent: CompiledStateGraph,
    smry_chain_wrapper: partial[Runnable],
    conversation_id: str,
    selected_model: str,
    chain_metadata: dict[str, Any],
):
    """Generate a title for the conversation."""
    smry_chain = smry_chain_wrapper(selected_model)

    config = {"configurable": {"thread_id": conversation_id}}
    state = await agent.aget_state(config)
    msgs: list[BaseMessage] = state.values.get("messages", [])

    title_raw: str = await smry_chain.ainvoke(
        input={"messages": msgs},
        config={"metadata": chain_metadata},
    )
    return title_raw.strip('"')
