from typing import Annotated, Optional

from fastapi import Depends, Header
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.chat import (
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from chatbot.config import settings
from chatbot.history import ContextAwareMessageHistory
from chatbot.memory import FlexConversationBufferWindowMemory
from chatbot.prompts.chatml import (
    AI_PREFIX,
    AI_SUFFIX,
    HUMAN_PREFIX,
    HUMAN_SUFFIX,
    ChatMLPromptTemplate,
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
        human_prefix=HUMAN_PREFIX,
        ai_prefix=AI_PREFIX,
        prefix_delimiter="\n",
        human_suffix=HUMAN_SUFFIX,
        ai_suffix=AI_SUFFIX,
        memory_key="history",
        input_key="input",
        chat_memory=history,
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
    system_prompt = PromptTemplate(
        template="""You are Rei, the ideal assistant dedicated to assisting users effectively.
Knowledge cutoff: 2023-10-01
Current date: {date}
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.""",
        input_variables=["date"],
    )
    messages = [
        SystemMessagePromptTemplate(prompt=system_prompt),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
    tmpl = ChatMLPromptTemplate(input_variables=["date", "input"], messages=messages)
    return LLMChain(
        llm=llm,
        prompt=tmpl,
        verbose=False,
        memory=memory,
    )
