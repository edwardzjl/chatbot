from fastapi import Header


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
