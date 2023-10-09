from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from langchain.chains import ConversationChain
from langchain.llms import BaseLLM, HuggingFaceTextGenInference
from langchain.memory import ConversationBufferWindowMemory, RedisChatMessageHistory
from loguru import logger

from chatbot.callbacks import (
    StreamingLLMCallbackHandler,
    UpdateConversationCallbackHandler,
)
from chatbot.config import settings
from chatbot.history import AppendSuffixHistory
from chatbot.prompts.vicuna import (
    prompt,
    human_prefix,
    ai_prefix,
    human_suffix,
    ai_suffix,
)
from chatbot.schemas import (
    ChatMessage,
    ConversationDetail,
    Conversation,
    UpdateConversation,
)
from chatbot.utils import UserIdHeader


router = APIRouter(
    prefix="/api",
    tags=["conversation"],
)


def get_message_history() -> RedisChatMessageHistory:
    return AppendSuffixHistory(
        url=settings.redis_om_url,
        user_suffix=human_suffix,
        ai_suffix=ai_suffix,
        session_id="sid",  # a fake session id as it is required
    )


def get_llm() -> BaseLLM:
    return HuggingFaceTextGenInference(
        inference_server_url=settings.inference_server_url,
        stop_sequences=["</s>", f"{human_prefix}:"],
        streaming=True,
    )


@router.get("/conversations", response_model=list[Conversation])
async def get_conversations(userid: Annotated[str | None, UserIdHeader()] = None):
    convs = await Conversation.find(Conversation.owner == userid).all()
    convs.sort(key=lambda x: x.updated_at, reverse=True)
    return convs


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    history: Annotated[RedisChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    conv = await Conversation.get(conversation_id)
    history.session_id = f"{userid}:{conversation_id}"
    return ConversationDetail(
        messages=[
            ChatMessage(
                conversation=conversation_id,
                from_="ai",
                content=message.content,
                type="text",
            ).model_dump()
            if message.type == "ai"
            else ChatMessage(
                conversation=conversation_id,
                from_=userid,
                content=message.content,
                type="text",
            ).model_dump()
            for message in history.messages
        ],
        **conv.model_dump(),
    )


@router.post("/conversations", status_code=201, response_model=ConversationDetail)
async def create_conversation(userid: Annotated[str | None, UserIdHeader()] = None):
    conv = Conversation(title=f"New chat", owner=userid)
    await conv.save()
    return conv


@router.put("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    payload: UpdateConversation,
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    conv = await Conversation.get(conversation_id)
    conv.title = payload.title
    await conv.save()


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await Conversation.delete(conversation_id)


@router.websocket("/chat")
async def generate(
    websocket: WebSocket,
    llm: Annotated[BaseLLM, Depends(get_llm)],
    history: Annotated[RedisChatMessageHistory, Depends(get_message_history)],
    userid: Annotated[str | None, UserIdHeader()] = None,
):
    await websocket.accept()
    memory = ConversationBufferWindowMemory(
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        memory_key="history",
        chat_memory=history,
    )
    conversation_chain: ConversationChain = ConversationChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )

    while True:
        try:
            payload: str = await websocket.receive_text()
            message = ChatMessage.model_validate_json(payload)
            history.session_id = f"{userid}:{message.conversation}"
            streaming_callback = StreamingLLMCallbackHandler(
                websocket, message.conversation
            )
            update_conversation_callback = UpdateConversationCallbackHandler(
                message.conversation
            )
            await conversation_chain.arun(
                message.content,
                callbacks=[streaming_callback, update_conversation_callback],
            )
        except WebSocketDisconnect:
            logger.info("websocket disconnected")
            return
        except Exception as e:
            logger.error(f"Something goes wrong, err: {e}")
