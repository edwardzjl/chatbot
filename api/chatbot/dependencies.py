from typing import Annotated, Optional

from fastapi import Depends, Header
from langchain.chains.base import Chain
from langchain_community.llms.huggingface_text_gen_inference import (
    HuggingFaceTextGenInference,
)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory

from chatbot.chains import ConversationChain, SummarizationChain
from chatbot.config import settings
from chatbot.history import ChatbotMessageHistory
from chatbot.memory import ChatbotMemory
from chatbot.prompts.chatml import AI_SUFFIX, HUMAN_PREFIX


def UserIdHeader(alias: Optional[str] = None, **kwargs):
    if alias is None:
        alias = settings.user_id_header
    return Header(alias=alias, **kwargs)


def UsernameHeader(alias: Optional[str] = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Preferred-Username"
    return Header(alias=alias, **kwargs)


def EmailHeader(alias: Optional[str] = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Email"
    return Header(alias=alias, **kwargs)


def MessageHistory() -> BaseChatMessageHistory:
    return ChatbotMessageHistory(
        url=str(settings.redis_om_url),
        key_prefix="chatbot:messages:",
        session_id="sid",  # a fake session id as it is required
    )


def ChatMemory(
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)]
) -> BaseMemory:
    return ChatbotMemory(
        memory_key="history",
        input_key="input",
        history=history,
        return_messages=True,
    )


def Llm() -> BaseLLM:
    return HuggingFaceTextGenInference(
        inference_server_url=str(settings.inference_server_url),
        max_new_tokens=1024,
        stop_sequences=[AI_SUFFIX, HUMAN_PREFIX],
        streaming=True,
    )


def ConvChain(
    llm: Annotated[BaseLLM, Depends(Llm)],
    memory: Annotated[BaseMemory, Depends(ChatMemory)],
) -> Chain:
    return ConversationChain(
        llm=llm,
        memory=memory,
    )


def SmryChain(
    llm: Annotated[BaseLLM, Depends(Llm)],
    memory: Annotated[BaseMemory, Depends(ChatMemory)],
) -> Chain:
    return SummarizationChain(
        llm=llm,
        memory=memory,
    )
