from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot

from chatbot.agent import create_agent
from chatbot.dependencies.commons import SettingsDep
from chatbot.dependencies.db import SqlalchemyEngineDep, get_raw_conn
from chatbot.http_client import HttpClient
from chatbot.llm.providers import LLMProvider, llm_provider_factory
from chatbot.tools.weather.openmeteo import WeatherTool

from .commons import get_http_client

if TYPE_CHECKING:
    from typing import AsyncGenerator


logger = logging.getLogger(__name__)


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
        from chatbot.tools.search.serpapi import SearchTool

        if settings.ipgeolocation_api_key:
            logger.info("Using IPGeolocation as geolocation tool.")
            from chatbot.tools.search.serpapi.geo import GeoLocationTool

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
    return tools


async def get_llm_provider(
    settings: SettingsDep,
    http_client: Annotated[HttpClient, Depends(get_http_client)],
) -> LLMProvider:
    provider = (settings.llm.metadata or {}).get("provider")
    return await llm_provider_factory(
        settings.llm.openai_api_base, provider, http_client
    )


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


async def get_agent(
    # chat_model: ChatModelDep,
    llm_provider: Annotated[LLMProvider, Depends(get_llm_provider)],
    checkpointer: Annotated[BaseCheckpointSaver, Depends(get_checkpointer)],
    tools: Annotated[list[BaseTool], Depends(get_tools)],
    # safety_model: SafetyModelDep,
    settings: SettingsDep,
) -> AsyncGenerator[CompiledGraph, None]:
    model_name = settings.llm.model_name
    context_length = await llm_provider.get_max_tokens(model_name)
    token_counter = llm_provider.get_token_counter(model_name)

    return create_agent(
        settings.llm,
        safety_model=settings.safety_llm,
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
def get_smry_chain(settings: SettingsDep) -> Runnable:
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
        | settings.llm.bind(
            extra_body={"chat_template_kwargs": {"enable_thinking": False}}
        )
        | StrOutputParser()
    )

    return runnable


SmrChainDep = Annotated[Runnable, Depends(get_smry_chain)]
