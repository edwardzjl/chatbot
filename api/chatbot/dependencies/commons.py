from aiohttp import ClientSession
from fastapi import Request, WebSocket


def get_client_session(
    request: Request = None, websocket: WebSocket = None
) -> ClientSession:
    """Get aiohttp session from scope.

    Scope can be either request or websocket.
    The session is global, and should be created in app lifespan.
    """
    scope = request or websocket
    session = getattr(scope.app.state, "aiohttp_session", None)
    if session is None:
        raise RuntimeError("aiohttp_session is not initialized in app.state.")
    return session
