from functools import cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Request, WebSocket

from chatbot.config import Settings
from chatbot.http_client import HttpClient


@cache
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


def uuid_or_404(param_name: str, resource_name: str = "Resource"):
    """Returns a dependency function that parses a UUID from the given path param.
    If the value is not a valid UUID, raises a 404 error with a detailed message.

    Args:
        param_name: The name of the path parameter (e.g. "conversation_id").
        resource_name: The display name of the resource for error messages (e.g. "Conversation").

    Returns:
        A dependency callable that returns a UUID or raises HTTP 404.
    """

    def dep(id_str: str = Path(..., alias=param_name)) -> UUID:
        try:
            return UUID(id_str)
        except ValueError:
            raise HTTPException(
                status_code=404, detail=f"{resource_name} [{id_str}] not found."
            )

    return Depends(dep)
