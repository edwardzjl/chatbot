"""Main entrypoint for the app."""

import logging
import re

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi_pagination import add_pagination

from prometheus_client import make_asgi_app
from starlette.routing import Mount

from chatbot.dependencies import EmailHeaderDep, UserIdHeaderDep, UsernameHeaderDep
from chatbot.dependencies.commons import SettingsDep
from chatbot.schemas import UserProfile
from chatbot.staticfiles import CompressedStaticFiles
from .exception_handlers import register_exception_handlers
from .lifespan import lifespan
from .routers import (
    chat_router,
    conv_router,
    files_router,
    message_router,
    probes_router,
    share_router,
)

logger = logging.getLogger(__name__)


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

app.include_router(chat_router, prefix="/api")
app.include_router(conv_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(message_router, prefix="/api")
app.include_router(probes_router, prefix="/api")
app.include_router(share_router, prefix="/api")


add_pagination(app)


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
    "/",
    CompressedStaticFiles(directory=STATIC_DIR, html=True, check_dir=False),
    name="static",
)


register_exception_handlers(app)


# return all unregistered, non-API call to web app
@app.exception_handler(404)
def spa_fallback(request: Request, _):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "API path not found"},
        )
    return FileResponse(f"{STATIC_DIR}/index.html")
