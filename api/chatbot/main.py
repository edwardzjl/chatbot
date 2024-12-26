"""Main entrypoint for the app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from loguru import logger
from prometheus_client import make_asgi_app
from sqlalchemy.exc import NoResultFound

from chatbot.config import settings
from chatbot.dependencies import EmailHeaderDep, UserIdHeaderDep, UsernameHeaderDep
from chatbot.models import Base
from chatbot.routers.chat import router as chat_router
from chatbot.routers.conversation import router as conversation_router
from chatbot.routers.message import router as message_router
from chatbot.routers.share import router as share_router
from chatbot.schemas import UserProfile
from chatbot.state import sqlalchemy_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables for ORM models
    async with sqlalchemy_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create checkpointer tables
    async with AsyncPostgresSaver.from_conn_string(
        settings.psycopg_primary_url
    ) as checkpointer:
        await checkpointer.setup()

    yield


app = FastAPI(
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add prometheus asgi middleware to route /metrics requests
metrics_app = make_asgi_app()
app.mount("/metrics/", metrics_app)


# NOTE: Even I mounted it to `/metrics`, I must append the trailing slash to access the metrics. i.e. `/metrics/`
# I think it's a bug in fastapi.
# My current solution is to add a redirect endpoint for this specific request.
@app.get("/metrics")
async def redirect_to_metrics_with_slash():
    return RedirectResponse(url="/metrics/")


app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(share_router)


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


app.mount(
    "/", StaticFiles(directory="static", html=True, check_dir=False), name="static"
)


@app.exception_handler(NoResultFound)
def not_found_error_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


templates = Jinja2Templates(directory="static")


# return all unregistered, non-API call to web app
@app.exception_handler(404)
def custom_404_handler(request: Request, _):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "API path not found"},
        )
    return templates.TemplateResponse("index.html", {"request": request})


@app.exception_handler(Exception)
def exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception("Unhandled error during request {}", request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "server error"},
    )
