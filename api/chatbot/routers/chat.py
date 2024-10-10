from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from langchain_core.messages import AIMessage, BaseMessage, trim_messages
from langgraph.graph.graph import CompiledGraph
from loguru import logger

from chatbot.chains.summarization import create_smry_chain
from chatbot.dependencies import UserIdHeader, get_agent
from chatbot.metrics.llm import input_tokens, output_tokens
from chatbot.models import Conversation
from chatbot.schemas import (
    AIChatMessage,
    AIChatStartMessage,
    AIChatEndMessage,
    ChatMessage,
    InfoMessage,
)
from chatbot.state import app_state
from chatbot.utils import utcnow

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    userid: Annotated[str | None, UserIdHeader()] = None,
    agent: CompiledGraph = Depends(get_agent),
):
    await websocket.accept()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            message = ChatMessage.model_validate_json(payload)
            async with app_state.sqlalchemy_session() as session:
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
            }
            async for event in agent.astream_events(
                input={"messages": [("user", message.content)]},
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
                logger.trace("event: {}", event)
                evt: str = event["event"]
                if evt == "on_chat_model_start":
                    msg = AIChatStartMessage(
                        parent_id=message.id,
                        id=event["run_id"],
                        conversation=message.conversation,
                    )
                    await websocket.send_text(msg.model_dump_json())
                if evt == "on_chat_model_stream":
                    msg = AIChatMessage(
                        parent_id=message.id,
                        id=event["run_id"],
                        conversation=message.conversation,
                        content=event["data"]["chunk"].content,
                        type="stream/text",
                    )
                    await websocket.send_text(msg.model_dump_json())
                if evt == "on_chat_model_end":
                    msg = AIChatEndMessage(
                        parent_id=message.id,
                        id=event["run_id"],
                        conversation=message.conversation,
                    )
                    await websocket.send_text(msg.model_dump_json())
                    msg: AIMessage = event["data"]["output"]
                    if msg.usage_metadata is not None:
                        input_tokens.labels(
                            user_id=userid,
                            model_name=msg.response_metadata["model_name"],
                        ).inc(msg.usage_metadata["input_tokens"])
                        output_tokens.labels(
                            user_id=userid,
                            model_name=msg.response_metadata["model_name"],
                        ).inc(msg.usage_metadata["output_tokens"])

            conv.last_message_at = utcnow()
            async with app_state.sqlalchemy_session() as session:
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
                smry_chain = create_smry_chain(app_state.chat_model)
                title_raw: str = await smry_chain.ainvoke(
                    input={"messages": windowed_messages},
                    config={"metadata": chain_metadata},
                )
                title = title_raw.strip('"')
                conv.title = title
                async with app_state.sqlalchemy_session() as session:
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
            return
        except Exception as e:
            logger.exception("Something goes wrong: {}", e)
