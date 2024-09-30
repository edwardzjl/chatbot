from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, WebSocketException
from langchain_core.messages import AIMessage
from loguru import logger
from prometheus_client import Counter

from chatbot.chains.conversation import conv_chain
from chatbot.chains.summarization import smry_chain
from chatbot.context import session_id
from chatbot.dependencies import UserIdHeader
from chatbot.memory import history
from chatbot.models import Conversation
from chatbot.schemas import (
    AIChatMessage,
    AIChatStartMessage,
    AIChatEndMessage,
    ChatMessage,
    InfoMessage,
)
from chatbot.utils import utcnow

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

input_tokens = Counter(
    "input_tokens", "Number of input tokens to the LLM", ["user_id", "model_name"]
)
output_tokens = Counter(
    "output_tokens",
    "Number of tokens generated by the LLM",
    ["user_id", "model_name"],
)


@router.websocket("")
async def chat(
    websocket: WebSocket,
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await websocket.accept()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            message = ChatMessage.model_validate_json(payload)
            conv = await Conversation.get(message.conversation)
            if conv.owner != userid:
                # TODO: I'm not sure whether this is the correct way to handle this.
                # See websocket code definitions here: <https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code>
                raise WebSocketException(code=3403, reason="authorization error")
            # set session_id early to ensure history is loaded correctly.
            session_id.set(f"{userid}:{message.conversation}")
            chain_metadata = {
                "conversation_id": message.conversation,
                "userid": userid,
            }
            async for event in conv_chain.astream_events(
                input={"input": message.content},
                config={
                    "run_name": "chat",
                    "metadata": chain_metadata,
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
                if event_name == "chat" and evt == "on_chain_end":
                    msg = AIChatMessage(
                        parent_id=message.id,
                        id=event["run_id"],
                        conversation=message.conversation,
                        content=event["data"]["output"],
                    )
                    await history.aadd_messages([message.to_lc(), msg.to_lc()])
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
            await conv.save()
            # summarize if required
            if message.additional_kwargs and message.additional_kwargs.get(
                "require_summarization", False
            ):
                title_raw: str = await smry_chain.ainvoke(
                    input={},
                    config={"metadata": chain_metadata},
                )
                title = title_raw.strip('"')
                conv.title = title
                await conv.save()
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
