from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Header
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.agent import create_agent
from chatbot.config import settings
from chatbot.llm_providers import get_truncation_config
from chatbot.state import sqlalchemy_ro_session, sqlalchemy_session
from .embeddings import HuggingfaceTEIEmbeddings

from langchain_core.embeddings import Embeddings
from langgraph.store.memory import InMemoryStore
# from langgraph.store.postgres import AsyncPostgresStore


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def UserIdHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-User"
    return Header(alias=alias, **kwargs)


UserIdHeaderDep = Annotated[str | None, UserIdHeader()]


def UsernameHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Preferred-Username"
    return Header(alias=alias, **kwargs)


UsernameHeaderDep = Annotated[str | None, UsernameHeader()]


def EmailHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Email"
    return Header(alias=alias, **kwargs)


EmailHeaderDep = Annotated[str | None, EmailHeader()]


async def get_sqlalchemy_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_session() as session:
        yield session


SqlalchemySessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_session)]


async def get_sqlalchemy_ro_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_ro_session() as session:
        yield session


SqlalchemyROSessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_ro_session)]


@lru_cache
def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(**settings.llm)


ChatModelDep = Annotated[ChatOpenAI, Depends(get_chat_model)]


@lru_cache
def get_safaty_model() -> ChatOpenAI | None:
    return (
        ChatOpenAI(**settings.safety_llm, tags=["internal"])
        if settings.safety_llm is not None
        else None
    )


SafetyModelDep = Annotated[ChatOpenAI, Depends(get_safaty_model)]


@lru_cache
def get_embeddings() -> Embeddings | None:
    return HuggingfaceTEIEmbeddings(
        base_url=str(settings.embeddings.url),
        truncate=True,
    ) if settings.embeddings else None

async def get_agent(
    chat_model: ChatModelDep,
    safety_model: SafetyModelDep,
    embeddings: Annotated[Embeddings | None, Depends(get_embeddings)],
) -> AsyncGenerator[CompiledGraph, None]:
    max_tokens, token_counter = get_truncation_config(
        settings.llm["base_url"], settings.llm["model_name"]
    )

    store = InMemoryStore(
        index={
            "embed": embeddings,
            "dims": settings.embeddings.dims,
            "fields": ["$"]
        }
    ) if embeddings else None

    async with AsyncPostgresSaver.from_conn_string(
        settings.psycopg_primary_url
    ) as checkpointer:
        yield create_agent(
            chat_model,
            safety_model=safety_model,
            checkpointer=checkpointer,
            store=store,
            token_counter=token_counter,
            max_tokens=max_tokens,
        )


AgentDep = Annotated[CompiledGraph, Depends(get_agent)]


async def get_agent_state(conversation_id: str, agent: AgentDep) -> StateSnapshot:
    config = {"configurable": {"thread_id": conversation_id}}
    return await agent.aget_state(config)


AgentStateDep = Annotated[StateSnapshot, Depends(get_agent_state)]


# I cannot apply `lru_cache` to this function for the following reasons:
# - `langchain_openai.ChatOpenAI` is not hashable. When type hinting it as `chat_model: ChatOpenAI = Depends(get_chat_model)`, Python raises the following error:
#   ```console
#   TypeError: unhashable type: 'ChatOpenAI'
#   ```
# - On the other hand, when I type hint it as `chat_model: ChatModelDep`, I encounter this error:
#   ```console
#   pydantic.errors.PydanticUndefinedAnnotation: name 'ChatModelDep' is not defined
#  ```
# So for now this function is not cached.
def get_smry_chain(chat_model: ChatModelDep) -> Runnable:
    instruction = (
        "You are Rei, the ideal assistant dedicated to assisting users effectively."
    )

    tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", instruction),
            ("placeholder", "{messages}"),
            (
                "system",
                "Now Provide a short summarization for the above messages in less than 10 words, using the same language as the user.",
            ),
        ]
    )

    return tmpl | chat_model | StrOutputParser()


SmrChainDep = Annotated[Runnable, Depends(get_smry_chain)]
