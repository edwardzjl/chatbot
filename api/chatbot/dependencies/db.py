from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from chatbot.dependencies.commons import get_settings


settings = get_settings()

sqlalchemy_engine = create_async_engine(
    str(settings.db_primary_url),
    poolclass=NullPool,
)
sqlalchemy_session = sessionmaker(
    sqlalchemy_engine,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_sqlalchemy_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_session() as session:
        yield session


SqlalchemySessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_session)]


@asynccontextmanager
async def get_raw_conn() -> AsyncGenerator[Any, None]:
    # See <https://docs.sqlalchemy.org/en/20/faq/connections.html#accessing-the-underlying-connection-for-an-asyncio-driver>
    async with sqlalchemy_engine.begin() as conn:
        # pep-249 style ConnectionFairy connection pool proxy object
        # presents a sync interface
        connection_fairy = await conn.get_raw_connection()

        # the really-real innermost driver connection is available
        # from the .driver_connection attribute
        raw_asyncio_connection = connection_fairy.driver_connection
        yield raw_asyncio_connection


sqlalchemy_ro_engine = create_async_engine(
    str(settings.db_standby_url),
    poolclass=NullPool,
)
sqlalchemy_ro_session = sessionmaker(
    sqlalchemy_ro_engine,
    autocommit=False,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_sqlalchemy_ro_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_ro_session() as session:
        yield session


SqlalchemyROSessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_ro_session)]
