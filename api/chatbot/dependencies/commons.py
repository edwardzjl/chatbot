from fastapi import Request, WebSocket

from chatbot.http_client import HttpClient


def get_http_client(request: Request = None, websocket: WebSocket = None) -> HttpClient:
    """Get aiohttp session from scope.

    Scope can be either request or websocket.
    The session is global, and should be created in app lifespan.
    """
    scope = request or websocket
    session = getattr(scope.app.state, "http_session", None)
    asession = getattr(scope.app.state, "aiohttp_session", None)

    return HttpClient(session=session, asession=asession)
