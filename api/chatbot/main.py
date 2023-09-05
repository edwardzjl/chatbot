"""Main entrypoint for the app."""
from contextlib import asynccontextmanager
from typing import Annotated

from aredis_om import Migrator, NotFoundError
from fastapi import FastAPI, Header, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import langchain
from langchain.cache import RedisCache
from loguru import logger
from redis import Redis

from chatbot.config import settings
from chatbot.routers import router


# TODO: should separate redis cache and storage instance
langchain.llm_cache = RedisCache(redis_=Redis.from_url(settings.redis_url))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Migrator().run()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/api/healthz")
def healthz():
    return "OK"


@app.get("/api/userinfo")
def userinfo(kubeflow_userid: Annotated[str | None, Header()] = None):
    return {"username": kubeflow_userid}


@app.exception_handler(NotFoundError)
async def notfound_exception_handler(request: Request, exc: NotFoundError):
    logger.error(f"NotFoundError: {exc}")
    # TODO: add some details here
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


app.mount(
    "/", StaticFiles(directory="static", html=True, check_dir=False), name="static"
)
