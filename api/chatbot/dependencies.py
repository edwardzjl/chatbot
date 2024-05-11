from operator import itemgetter
from typing import Optional

from fastapi import Header
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from chatbot.chains import ConversationChain
from chatbot.chains.summarization import tmpl
from chatbot.config import settings
from chatbot.memory import ChatbotMemory
from chatbot.memory.history import ChatbotMessageHistory


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


llm = ChatOpenAI(
    openai_api_base=str(settings.llm.url),
    model=settings.llm.model,
    openai_api_key=settings.llm.creds,
    max_tokens=1024,
    streaming=True,
)

history = ChatbotMessageHistory(
    url=str(settings.redis_om_url),
    key_prefix="chatbot:messages:",
    session_id="sid",  # a fake session id as it is required
)

memory = ChatbotMemory(
    memory_key="history",
    input_key="input",
    history=history,
    return_messages=True,
)

conv_chain = ConversationChain(
    llm=llm,
    memory=memory,
)

smry_chain = (
    {
        "history": RunnableLambda(
            memory.load_memory_variables, afunc=memory.aload_memory_variables
        )
        | itemgetter("history")
    }
    | tmpl
    | llm
    | StrOutputParser()
)
