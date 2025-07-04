from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import cache
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from chatbot.dependencies.commons import SettingsDep


@cache
def create_engine(settings: SettingsDep) -> AsyncEngine:
    return create_async_engine(
        str(settings.db_primary_url),
        poolclass=NullPool,
    )


SqlalchemyEngineDep = Annotated[AsyncEngine, Depends(create_engine)]


@cache
def create_sessionmaker(
    engine: SqlalchemyEngineDep,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        autocommit=False,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


SqlalchemySessionMakerDep = Annotated[
    async_sessionmaker[AsyncSession], Depends(create_sessionmaker)
]


async def get_sqlalchemy_session(
    session_maker: SqlalchemySessionMakerDep,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


SqlalchemySessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_session)]


@asynccontextmanager
async def get_raw_conn(engine: SqlalchemyEngineDep) -> AsyncGenerator[Any, None]:
    # See <https://docs.sqlalchemy.org/en/20/faq/connections.html#accessing-the-underlying-connection-for-an-asyncio-driver>
    async with engine.begin() as conn:
        # pep-249 style ConnectionFairy connection pool proxy object
        # presents a sync interface
        connection_fairy = await conn.get_raw_connection()

        # the really-real innermost driver connection is available
        # from the .driver_connection attribute
        raw_asyncio_connection = connection_fairy.driver_connection
        yield raw_asyncio_connection


@cache
def create_ro_engine(settings: SettingsDep) -> AsyncEngine:
    kwargs = {}
    if settings.db_standby_url.scheme.startswith("postgres"):
        kwargs["isolation_level"] = "REPEATABLE READ"
    return create_async_engine(
        str(settings.db_standby_url),
        poolclass=NullPool,
        **kwargs,
    )


SqlalchemyROEngineDep = Annotated[AsyncEngine, Depends(create_ro_engine)]


@cache
def create_ro_sessionmaker(
    engine: Annotated[AsyncEngine, Depends(create_ro_engine)],
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        autocommit=False,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )


async def get_sqlalchemy_ro_session(
    session_maker: Annotated[
        async_sessionmaker[AsyncSession], Depends(create_ro_sessionmaker)
    ],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


SqlalchemyROSessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_ro_session)]
