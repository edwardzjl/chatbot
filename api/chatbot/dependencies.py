from collections.abc import AsyncGenerator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.state import app_state


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
