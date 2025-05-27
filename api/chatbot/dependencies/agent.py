from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from functools import partial
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot

from chatbot.agent import create_agent
from chatbot.dependencies.commons import SettingsDep
from chatbot.dependencies.db import SqlalchemyEngineDep, get_raw_conn
from chatbot.http_client import HttpClient
from chatbot.tools import BrowserTool, GeoLocationTool, SearchTool, WeatherTool


from .commons import get_http_client


logger = logging.getLogger(__name__)


def ModelHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "Select-Model"
    return Header(alias=alias, **kwargs)


# Cannot apply `lru_cache` to this function:
def get_tools(
    settings: SettingsDep,
    http_client: Annotated[HttpClient, Depends(get_http_client)],
) -> list[BaseTool]:
    tools = []
    tools.append(
        WeatherTool(http_client=http_client, apikey=settings.openmeteo_api_key)
    )
    if settings.serp_api_key:
        logger.info("Using SerpApi as search tool.")

        if settings.ipgeolocation_api_key:
            logger.info("Using IPGeolocation as geolocation tool.")

            geo_tool = GeoLocationTool(
                api_key=settings.ipgeolocation_api_key, http_client=http_client
            )
        else:
            geo_tool = None
        tools.append(
            SearchTool(
                api_key=settings.serp_api_key,
                http_client=http_client,
                geo_tool=geo_tool,
            )
        )
    tools.append(BrowserTool(http_client=http_client))
    return tools


@asynccontextmanager
async def get_checkpointer(
    settings: SettingsDep,
    engine: SqlalchemyEngineDep,
) -> AsyncGenerator[BaseCheckpointSaver, None]:
    if settings.db_primary_url.startswith("postgresql"):
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        async with get_raw_conn(engine) as conn:
            yield AsyncPostgresSaver(conn)

    elif settings.db_primary_url.startswith("sqlite"):
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        async with get_raw_conn(engine) as conn:
            yield AsyncSqliteSaver(conn)
    else:
        from langgraph.checkpoint.memory import InMemorySaver

        yield InMemorySaver()


@asynccontextmanager
async def get_agent(
    engine: SqlalchemyEngineDep,
    tools: Annotated[list[BaseTool], Depends(get_tools)],
    settings: SettingsDep,
    select_model: Annotated[str | None, ModelHeader()] = None,
) -> AsyncGenerator[CompiledGraph, None]:
    llm = settings.must_get_llm(select_model)

    async with get_checkpointer(settings, engine) as checkpointer:
        # Cannot use return here, or the connection will be closed.
        yield create_agent(
            llm,
            safety_model=settings.safety_llm,
            checkpointer=checkpointer,
            tools=tools,
        )


def get_agent_wrapper(
    engine: SqlalchemyEngineDep,
    tools: Annotated[list[BaseTool], Depends(get_tools)],
    settings: SettingsDep,
) -> partial[AsyncGenerator[CompiledGraph, None]]:
    return partial(get_agent, engine, tools, settings)


AgentWrapperDep = Annotated[
    partial[AsyncGenerator[CompiledGraph, None]], Depends(get_agent_wrapper)
]


async def get_agent_for_state(
    engine: SqlalchemyEngineDep,
    settings: SettingsDep,
) -> AsyncGenerator[CompiledGraph, None]:
    """Get an agent only for accessing the state.

    Only the checkpointer is needed in such usecase.

    Do NOT use this agent for any other purpose.
    """
    # A whatever LLM.
    llm = ChatOpenAI(openai_api_key="whatever")
    async with get_checkpointer(settings, engine) as checkpointer:
        # Cannot use return here, or the connection will be closed.
        yield create_agent(
            llm,
            checkpointer=checkpointer,
        )


AgentForStateDep = Annotated[
    AsyncGenerator[CompiledGraph, None], Depends(get_agent_for_state)
]


# A simple wrapper when you have access to `conversation_id` in the endpoint.
async def get_agent_state(
    conversation_id: str, agent: AgentForStateDep
) -> StateSnapshot:
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
def get_smry_chain(
    settings: SettingsDep,
    select_model: Annotated[str | None, ModelHeader()] = None,
) -> Runnable:
    llm = settings.must_get_llm(select_model)

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

    runnable = (
        tmpl
        | llm.bind(extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        | StrOutputParser()
    )

    return runnable


SmrChainDep = Annotated[Runnable, Depends(get_smry_chain)]


def get_smry_chain_wrapper(settings: SettingsDep) -> partial[Runnable]:
    return partial(get_smry_chain, settings)


SmrChainWrapperDep = Annotated[partial[Runnable], Depends(get_smry_chain_wrapper)]
