from contextlib import asynccontextmanager
from inspect import iscoroutinefunction
from functools import partial

from aiohttp import ClientTimeout
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from fastapi import FastAPI
from langgraph.checkpoint.base import BaseCheckpointSaver
from requests_cache import CachedSession

from chatbot.dependencies.commons import get_settings
from chatbot.dependencies.db import create_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    sqlalchemy_engine = create_engine(settings)
    autocommit_engine = sqlalchemy_engine.execution_options(
        isolation_level="AUTOCOMMIT"
    )

    async with autocommit_engine.begin() as conn:
        if settings.db_primary_url.scheme.startswith("postgresql"):
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            connection_fairy = await conn.get_raw_connection()
            raw_asyncio_connection = connection_fairy.driver_connection
            checkpointer = AsyncPostgresSaver(raw_asyncio_connection)

        elif settings.db_primary_url.scheme.startswith("sqlite"):
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

            connection_fairy = await conn.get_raw_connection()
            raw_asyncio_connection = connection_fairy.driver_connection
            checkpointer = AsyncSqliteSaver(raw_asyncio_connection)
        else:
            from langgraph.checkpoint.memory import InMemorySaver

            checkpointer = InMemorySaver()
        await maybe_setup_checkpointer(checkpointer)

    app.state.http_session = CachedSession(
        expire_after=-1, ignored_parameters=["api_key", "apikey"], use_temp=True
    )
    app.state.http_session.request = partial(app.state.http_session.request, timeout=10)

    app.state.aiohttp_session = AsyncCachedSession(
        timeout=ClientTimeout(total=10),
        raise_for_status=True,
        cache=SQLiteBackend(use_temp=True),
    )

    yield

    app.state.http_session.close()
    await app.state.aiohttp_session.close()


async def maybe_setup_checkpointer(checkpointer: BaseCheckpointSaver) -> None:
    """Set up the checkpointer, if applicable.

    Some checkpointer implementations (e.g., `langgraph.checkpoint.postgres.PostgresSaver`)
    provide a `setup()` method, which may be either synchronous or asynchronous
    (e.g., `langgraph.checkpoint.postgres.aio.AsyncPostgresSaver`).

    This utility detects and invokes the appropriate `setup()` method if it exists,
    allowing for a unified setup process across different checkpointer types.
    """

    setup = getattr(checkpointer, "setup", None)
    if setup is None:
        return

    if iscoroutinefunction(setup):
        await setup()
    else:
        setup()
