"""Main entrypoint for the app."""

import logging
import re
from contextlib import asynccontextmanager
from inspect import iscoroutinefunction
from functools import partial

from aiohttp import ClientTimeout
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from langgraph.checkpoint.base import BaseCheckpointSaver
from prometheus_client import make_asgi_app
from requests_cache import CachedSession
from sqlalchemy.exc import NoResultFound
from starlette.routing import Mount

from chatbot.dependencies import EmailHeaderDep, UserIdHeaderDep, UsernameHeaderDep
from chatbot.dependencies.commons import SettingsDep, get_settings
from chatbot.dependencies.db import create_engine
from chatbot.models import Base
from chatbot.routers.chat import router as chat_router
from chatbot.routers.conversation import router as conversation_router
from chatbot.routers.files import router as files_router
from chatbot.routers.message import router as message_router
from chatbot.routers.share import router as share_router
from chatbot.schemas import UserProfile


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    sqlalchemy_engine = create_engine(settings)
    # Create tables for ORM models
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Create checkpointer tables
        if settings.db_primary_url.startswith("postgresql"):
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            connection_fairy = await conn.get_raw_connection()
            raw_asyncio_connection = connection_fairy.driver_connection
            checkpointer = AsyncPostgresSaver(raw_asyncio_connection)

        elif settings.db_primary_url.startswith("sqlite"):
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

            connection_fairy = await conn.get_raw_connection()
            raw_asyncio_connection = connection_fairy.driver_connection
            checkpointer = AsyncSqliteSaver(raw_asyncio_connection)
        else:
            from langgraph.checkpoint.memory import InMemorySaver

            checkpointer = InMemorySaver()
        await maybe_setup_checkpointer(checkpointer)

    app.state.http_session = CachedSession(
        expire_after=-1, ignored_parameters=["api_key", "apikey"], use_temp=True
    )
    app.state.http_session.request = partial(app.state.http_session.request, timeout=10)

    app.state.aiohttp_session = AsyncCachedSession(
        timeout=ClientTimeout(total=10),
        raise_for_status=True,
        cache=SQLiteBackend(use_temp=True),
    )

    yield

    app.state.http_session.close()
    await app.state.aiohttp_session.close()


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add prometheus asgi middleware to route /metrics requests
metrics_route = Mount("/metrics", make_asgi_app())
# @See https://github.com/prometheus/client_python/issues/1016#issuecomment-2088243791
# @See https://github.com/vllm-project/vllm/pull/4511#issuecomment-2088375895
metrics_route.path_regex = re.compile("^/metrics(?P<path>.*)$")
app.routes.append(metrics_route)

app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(share_router)
app.include_router(files_router)


add_pagination(app)


@app.get("/api/healthz")
def healthz():
    return "OK"


@app.get("/api/userinfo")
def userinfo(
    userid: UserIdHeaderDep,
    username: UsernameHeaderDep,
    email: EmailHeaderDep,
) -> UserProfile:
    return UserProfile(
        userid=userid,
        username=username,
        email=email,
    )


@app.get("/api/models")
def models_info(settings: SettingsDep) -> list[dict]:
    return [llm.to_json() for llm in settings.llms]


STATIC_DIR = "static"


app.mount(
    "/", StaticFiles(directory=STATIC_DIR, html=True, check_dir=False), name="static"
)


@app.exception_handler(NoResultFound)
def not_found_error_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


# return all unregistered, non-API call to web app
@app.exception_handler(404)
def spa_fallback(request: Request, _):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "API path not found"},
        )
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception("Unhandled error during request %s", request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "server error"},
    )


async def maybe_setup_checkpointer(checkpointer: BaseCheckpointSaver) -> None:
    """Set up the checkpointer, if applicable.

    Some checkpointer implementations (e.g., `langgraph.checkpoint.postgres.PostgresSaver`)
    provide a `setup()` method, which may be either synchronous or asynchronous
    (e.g., `langgraph.checkpoint.postgres.aio.AsyncPostgresSaver`).

    This utility detects and invokes the appropriate `setup()` method if it exists,
    allowing for a unified setup process across different checkpointer types.
    """

    setup = getattr(checkpointer, "setup", None)
    if setup is None:
        return

    if iscoroutinefunction(setup):
        await setup()
    else:
        setup()
