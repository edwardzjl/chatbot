from typing import Annotated, Optional

from fastapi import Depends, Header
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory

from chatbot.config import settings
from chatbot.history import ContextAwareMessageHistory
from chatbot.memory import FlexConversationBufferWindowMemory
from chatbot.prompts.chatml import (
    ai_prefix,
    ai_suffix,
    human_prefix,
    human_suffix,
    prompt,
)


def UserIdHeader(alias: Optional[str] = None, **kwargs):
    if alias is None:
        alias = settings.user_id_header
    return Header(alias=alias, **kwargs)


def MessageHistory() -> BaseChatMessageHistory:
    return ContextAwareMessageHistory(
        url=str(settings.redis_om_url),
        key_prefix="chatbot:messages:",
        session_id="sid",  # a fake session id as it is required
    )


def ChatMemory(
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)]
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


def Llm() -> BaseLLM:
    return HuggingFaceTextGenInference(
        inference_server_url=str(settings.inference_server_url),
        max_new_tokens=1024,
        stop_sequences=[ai_suffix, human_prefix],
        streaming=True,
    )


def ConvChain(
    llm: Annotated[BaseLLM, Depends(Llm)],
    memory: Annotated[BaseMemory, Depends(ChatMemory)],
) -> Chain:
    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )
