from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Annotated, Any
from urllib.parse import urljoin

import requests
from fastapi import Depends, Header
from langchain_core.messages.utils import convert_to_openai_messages
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.agent import create_agent
from chatbot.config import settings
from chatbot.state import sqlalchemy_ro_session, sqlalchemy_session

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


# TODO: we can support async here, but I'm not explicitly depending on `aiohttp` yet.
@lru_cache
def get_model_info() -> dict[str, Any]:
    url = urljoin(settings.llm["base_url"], "/v1/models")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        # NOTE: this is based on vllm, IDK what the response of OpenAI looks like.
        models = resp.json().get("data", [])

        return next(
            (item for item in models if item["id"] == settings.llm["model_name"]), {}
        )

    except requests.RequestException:
        logger.warning("Error loading model info")
        raise


# TODO: langchain's `get_num_tokens_from_messages` does not support async
def get_num_tokens_vllm(messages: list) -> int:
    """Get the number of tokens in a list of messages."""
    url = urljoin(settings.llm["base_url"], "/tokenize")
    # use 'prompt' param instead of 'messages' to get the number of tokens in the prompt
    try:
        resp = requests.post(
            url,
            json={
                "model": settings.llm["model_name"],
                "messages": convert_to_openai_messages(messages),
            },
        )
        resp.raise_for_status()
        return resp.json()["count"]
    except requests.RequestException as e:
        logger.warning("Error loading model info: {}", str(e))
        # Default to 0 if there is an error
        return 0


async def get_agent(
    chat_model: ChatModelDep,
    safety_model: SafetyModelDep,
    model_info: Annotated[dict[str, Any], Depends(get_model_info)],
) -> AsyncGenerator[CompiledGraph, None]:
    async with AsyncPostgresSaver.from_conn_string(
        settings.psycopg_primary_url
    ) as checkpointer:
        yield create_agent(
            chat_model,
            safety_model=safety_model,
            checkpointer=checkpointer,
            token_counter=get_num_tokens_vllm,
            # NOTE: this is based on vllm, IDK what the response of OpenAI looks like.
            max_tokens=model_info["max_model_len"],
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
