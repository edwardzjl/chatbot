import logging

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from langchain_core.messages import AIMessage, BaseMessage, trim_messages

from chatbot.dependencies import AgentDep, SmrChainDep, UserIdHeaderDep
from chatbot.dependencies.db import sqlalchemy_session
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
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    userid: UserIdHeaderDep,
    agent: AgentDep,
    smry_chain: SmrChainDep,
):
    await websocket.accept()
    connected_clients.inc()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            message = HumanChatMessage.model_validate_json(payload)
            async with sqlalchemy_session() as session:
                conv: Conversation = await session.get(
                    Conversation, message.conversation
                )
            if conv.owner != userid:
                # TODO: I'm not sure whether this is the correct way to handle this.
                # See websocket code definitions here: <https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code>
                raise WebSocketException(code=3403, reason="authorization error")
            chain_metadata = {
                "conversation_id": message.conversation,
                "userid": userid,
                "client_ip": websocket.client.host,
            }
            async for event in agent.astream_events(
                input={"messages": [message.to_lc()]},
                config={
                    "run_name": "chat",
                    "metadata": chain_metadata,
                    "configurable": {"thread_id": message.conversation},
                },
                version="v2",
            ):
                event_name: str = event["name"]
                if event_name.startswith("_"):
                    # events starts with "_" are langchain's internal events, for example '_Exception'
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
                        id=f"run-{event['run_id']}",
                        conversation=message.conversation,
                        content="",  # Tired of handling null / undefined in js, simply sending an empty string.
                    )
                    await websocket.send_text(msg.model_dump_json())
                if evt == "on_chat_model_stream":
                    msg = ChatMessage.from_lc(event["data"]["chunk"])
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

            conv.last_message_at = utcnow()
            async with sqlalchemy_session() as session:
                conv = await session.merge(conv)
                await session.commit()

            # summarize if required
            if message.additional_kwargs and message.additional_kwargs.get(
                "require_summarization", False
            ):
                config = {"configurable": {"thread_id": message.conversation}}
                state = await agent.aget_state(config)
                msgs: list[BaseMessage] = state.values.get("messages", [])

                windowed_messages = trim_messages(
                    msgs,
                    token_counter=len,
                    max_tokens=20,
                    start_on="human",  # This means that the first message should be from the user after trimming.
                )
                title_raw: str = await smry_chain.ainvoke(
                    input={"messages": windowed_messages},
                    config={"metadata": chain_metadata},
                )
                title = title_raw.strip('"')
                conv.title = title
                async with sqlalchemy_session() as session:
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
