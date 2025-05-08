from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request, WebSocket

from chatbot.config import Settings
from chatbot.http_client import HttpClient


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=[".env"], _env_file_encoding="utf-8")


SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_http_client(request: Request = None, websocket: WebSocket = None) -> HttpClient:
    """Get aiohttp session from scope.

    Scope can be either request or websocket.
    The session is global, and should be created in app lifespan.
    """
    scope = request or websocket
    session = getattr(scope.app.state, "http_session", None)
    asession = getattr(scope.app.state, "aiohttp_session", None)

    return HttpClient(session=session, asession=asession)
