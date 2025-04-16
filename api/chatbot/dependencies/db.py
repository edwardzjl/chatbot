from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.state import sqlalchemy_ro_session, sqlalchemy_session


async def get_sqlalchemy_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_session() as session:
        yield session


SqlalchemySessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_session)]


async def get_sqlalchemy_ro_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlalchemy_ro_session() as session:
        yield session


SqlalchemyROSessionDep = Annotated[AsyncSession, Depends(get_sqlalchemy_ro_session)]
