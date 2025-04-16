from __future__ import annotations

from typing import Annotated

from fastapi import Header


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
