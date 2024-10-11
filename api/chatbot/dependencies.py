from typing import Annotated
from collections.abc import AsyncGenerator

from fastapi import Depends, Header
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.types import StateSnapshot
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.agent import create_agent
from chatbot.config import settings
from chatbot.state import chat_model, sqlalchemy_session, sqlalchemy_ro_session


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


async def get_agent() -> AsyncGenerator[CompiledGraph, None]:
    async with AsyncPostgresSaver.from_conn_string(
        settings.psycopg_primary_url
    ) as checkpointer:
        yield create_agent(chat_model, checkpointer)


AgentDep = Annotated[CompiledGraph, Depends(get_agent)]


async def get_agent_state(
    conversation_id: str,
    agent: Annotated[CompiledGraph, Depends(get_agent)],
) -> StateSnapshot:
    config = {"configurable": {"thread_id": conversation_id}}
    return await agent.aget_state(config)


AgentStateDep = Annotated[StateSnapshot, Depends(get_agent_state)]
