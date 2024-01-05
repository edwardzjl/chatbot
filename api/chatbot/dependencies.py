from typing import Annotated, Optional

from fastapi import Depends, Header
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.memory import (
    CombinedMemory,
    ConversationBufferWindowMemory,
    VectorStoreRetrieverMemory,
)

from langchain_community.llms.huggingface_text_gen_inference import (
    HuggingFaceTextGenInference,
)
from langchain_community.vectorstores.redis import Redis
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models import BaseLLM
from langchain_core.memory import BaseMemory
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)

from chatbot.callbacks import TracingLLMCallbackHandler
from chatbot.chains import LLMConvChain
from chatbot.config import settings
from chatbot.embeddings import HuggingfaceTEIEmbeddings
from chatbot.memory import ConversationRetrieverMemory
from chatbot.history import ContextAwareMessageHistory
from chatbot.prompts.chatml import AI_SUFFIX, HUMAN_PREFIX, ChatMLPromptTemplate


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
    return ContextAwareMessageHistory(
        url=str(settings.redis_om_url),
        key_prefix="chatbot:messages:",
        session_id="sid",  # a fake session id as it is required
    )


def ChatMemory(
    history: Annotated[BaseChatMessageHistory, Depends(MessageHistory)]
) -> BaseMemory:
    return ConversationBufferWindowMemory(
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
        callbacks=[TracingLLMCallbackHandler()],
    )


def ConvChain(
    llm: Annotated[BaseLLM, Depends(Llm)],
    short_memory: Annotated[BaseMemory, Depends(ChatMemory)],
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
        SystemMessagePromptTemplate.from_template(
            "Following are some relevant pieces of previous conversation (Feel free to ignore them if they are not relevant to the current conversation):"
        ),
        MessagesPlaceholder(variable_name="deep_history"),
        SystemMessagePromptTemplate.from_template("Current conversation:"),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
    tmpl = ChatMLPromptTemplate(input_variables=["date", "input"], messages=messages)

    embedding = HuggingfaceTEIEmbeddings(
        base_url=str(settings.embedding_url),
        query_instruction="为这个句子生成表示以用于检索相关文章：",  # TODO:
    )
    vectorstore = Redis(
        redis_url=str(settings.redis_om_url),
        embedding=embedding,
        index_name="chatbot:memories",
        key_prefix="chatbot:memories",
        index_schema={"text": [{"name": "input"}, {"name": "text"}]},
        vector_schema={"algorithm": "HNSW"},
    )
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 1, "distance_threshold": 0.9}
    )
    deep_memory = ConversationRetrieverMemory(
        retriever=retriever,
        memory_key="deep_history",
        input_key="input",
        output_key="text",
        exclude_input_keys=["date", "history"],
        return_messages=True,
    )
    memory = CombinedMemory(memories=[deep_memory, short_memory])
    return LLMChain(
        # user_input_variable="input",
        llm=llm,
        prompt=tmpl,
        verbose=False,
        memory=memory,
    )
