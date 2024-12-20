"""Main entrypoint for the app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
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
# NOTE: although I mount it to `/metrics`, you must append the trailing slash to access the metrics. i.e. `/metrics/`
# I think it's a bug in fastapi
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

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


@app.exception_handler(NoResultFound)
async def not_found_error_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


app.mount(
    "/", StaticFiles(directory="static", html=True, check_dir=False), name="static"
)

templates = Jinja2Templates(directory="static")


# return all unregistered, non-API call to web app
@app.exception_handler(404)
async def custom_404_handler(request: Request, _):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "API path not found"},
        )
    return templates.TemplateResponse("index.html", {"request": request})
