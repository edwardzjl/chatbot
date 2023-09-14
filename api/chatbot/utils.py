from datetime import datetime, timezone
from typing import Optional

from fastapi import Header

from chatbot.config import settings


def UserIdHeader(alias: Optional[str] = None, **kwargs):
    if alias is None:
        alias = settings.user_id_header
    return Header(alias=alias, **kwargs)


def utcnow():
    """
    datetime.datetime.utcnow() does not contain timezone information.
    """
    return datetime.now(timezone.utc)
