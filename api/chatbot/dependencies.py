from collections.abc import AsyncGenerator

from fastapi import Header
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.graph import CompiledGraph
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.agent import create_agent
from chatbot.config import settings
from chatbot.state import app_state
from chatbot.utils import remove_driver


def UserIdHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-User"
    return Header(alias=alias, **kwargs)


def UsernameHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Preferred-Username"
    return Header(alias=alias, **kwargs)


def EmailHeader(alias: str | None = None, **kwargs):
    if alias is None:
        alias = "X-Forwarded-Email"
    return Header(alias=alias, **kwargs)


async def get_sqlalchemy_session() -> AsyncGenerator[AsyncSession, None]:
    async with app_state.sqlalchemy_session() as session:
        yield session


async def get_agent() -> AsyncGenerator[CompiledGraph, None]:
    async with AsyncPostgresSaver.from_conn_string(
        remove_driver(str(settings.db_url))
    ) as checkpointer:
        yield create_agent(app_state.chat_model, checkpointer)
