from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms import BaseLLM, HuggingFaceTextGenInference
from langchain.memory import RedisChatMessageHistory
from langchain.schema import BaseMemory
from loguru import logger

from chatbot.callbacks import (
    StreamingLLMCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.config import settings
from chatbot.context import session_id
from chatbot.history import ContextAwareMessageHistory
from chatbot.memory import FlexConversationBufferWindowMemory
from chatbot.models import Conversation as ORMConversation
from chatbot.prompts.chatml import (
    ai_prefix,
    ai_suffix,
    human_prefix,
    human_suffix,
    prompt,
)
from chatbot.schemas import (
    ChatMessage,
    Conversation,
    ConversationDetail,
    UpdateConversation,
)
from chatbot.utils import UserIdHeader

router = APIRouter(
    prefix="/api",
    tags=["conversation"],
)


def get_message_history() -> RedisChatMessageHistory:
    return ContextAwareMessageHistory(
        url=str(settings.redis_om_url),
        session_id="sid",  # a fake session id as it is required
    )


def get_memory(
    history: Annotated[RedisChatMessageHistory, Depends(get_message_history)]
) -> BaseMemory:
    return FlexConversationBufferWindowMemory(
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        prefix_delimiter="\n",
        human_suffix=human_suffix,
        ai_suffix=ai_suffix,
        memory_key="history",
        input_key="input",
        chat_memory=history,
    )


def get_llm() -> BaseLLM:
    return HuggingFaceTextGenInference(
        inference_server_url=str(settings.inference_server_url),
        stop_sequences=[ai_suffix, human_prefix],
        streaming=True,
    )


def get_conv_chain(
    llm: Annotated[BaseLLM, Depends(get_llm)],
    memory: Annotated[BaseMemory, Depends(get_memory)],
) -> Chain:
    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )


@router.get("/conversations")
async def get_conversations(
    userid: Annotated[str | None, UserIdHeader()] = None
) -> list[Conversation]:
    convs = await ORMConversation.find(ORMConversation.owner == userid).all()
    convs.sort(key=lambda x: x.updated_at, reverse=True)
    return [Conversation(**conv.dict()) for conv in convs]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    history: Annotated[RedisChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> ConversationDetail:
    conv = await ORMConversation.get(conversation_id)
    session_id.set(f"{userid}:{conversation_id}")
    return ConversationDetail(
        messages=[
            ChatMessage.from_lc(lc_message=message, conv_id=conversation_id, from_="ai")
            if message.type == "ai"
            else ChatMessage.from_lc(
                lc_message=message, conv_id=conversation_id, from_=userid
            )
            for message in history.messages
        ],
        **conv.dict(),
    )


@router.post("/conversations", status_code=201)
async def create_conversation(
    userid: Annotated[str | None, UserIdHeader()] = None
) -> ConversationDetail:
    conv = ORMConversation(title=f"New chat", owner=userid)
    await conv.save()
    return ConversationDetail(**conv.dict())


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    conv = await ORMConversation.get(conversation_id)
    conv.title = payload.title
    await conv.save()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
) -> None:
    await ORMConversation.delete(conversation_id)


@router.websocket("/chat")
async def generate(
    websocket: WebSocket,
    conv_chain: Annotated[LLMChain, Depends(get_conv_chain)],
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await websocket.accept()
    logger.info("websocket connected")
    while True:
        try:
            payload: str = await websocket.receive_text()
            system_message = f"""You are Mistral-OpenOrca, a large language model trained by Open-Orca. Answer as concisely as possible.
Knowledge cutoff: 2023-10-01
Current date: {date.today()}"""
            message = ChatMessage.model_validate_json(payload)
            session_id.set(f"{userid}:{message.conversation}")
            streaming_callback = StreamingLLMCallbackHandler(
                websocket, message.conversation
            )
            update_conversation_callback = UpdateConversationCallbackHandler(
                message.conversation
            )
            await conv_chain.arun(
                system_message=system_message,
                input=message.content,
                callbacks=[streaming_callback, update_conversation_callback],
            )
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            return
        except Exception as e:
            logger.error(f"Something goes wrong, err: {e}")
