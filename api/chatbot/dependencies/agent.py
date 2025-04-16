from __future__ import annotations

import logging
from functools import lru_cache
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot

from chatbot.agent import create_agent
from chatbot.config import settings
from chatbot.llm.client import ReasoningChatOpenai
from chatbot.llm.providers import get_truncation_config
from chatbot.tools.weather.openmeteo import WeatherTool

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


logger = logging.getLogger(__name__)


@lru_cache
def get_chat_model() -> ChatOpenAI:
    return ReasoningChatOpenai(**settings.llm)


ChatModelDep = Annotated[ChatOpenAI, Depends(get_chat_model)]


@lru_cache
def get_safaty_model() -> ChatOpenAI | None:
    return (
        ChatOpenAI(**settings.safety_llm, tags=["internal"])
        if settings.safety_llm is not None
        else None
    )


SafetyModelDep = Annotated[ChatOpenAI, Depends(get_safaty_model)]


async def get_agent(
    chat_model: ChatModelDep,
    safety_model: SafetyModelDep,
) -> AsyncGenerator[CompiledGraph, None]:
    context_length, token_counter = await get_truncation_config(
        settings.llm["base_url"], settings.llm["model_name"]
    )
    if settings.serp_api_key:
        logger.info("Using SerpApi as search tool.")
        from chatbot.tools.search.serpapi import SearchTool

        tools = [WeatherTool(), SearchTool(api_key=settings.serp_api_key)]
    else:
        tools = [WeatherTool()]

    async with AsyncPostgresSaver.from_conn_string(
        settings.psycopg_primary_url
    ) as checkpointer:
        yield create_agent(
            chat_model,
            safety_model=safety_model,
            checkpointer=checkpointer,
            token_counter=token_counter,
            context_length=context_length,
            tools=tools,
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
