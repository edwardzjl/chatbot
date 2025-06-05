import asyncio
import logging
import os
import sys


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="datetime=%(asctime)s level=%(levelname)s filename=%(filename)s module=%(module)s name=%(name)s lineno=%(lineno)s message=%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class EndpointFilter(logging.Filter):
    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


paths_to_filter = [
    # API doc endpoints
    "/api/openapi.json",
    "/api/docs",
    "/api/redoc",
    # probe and metric endpoints
    "/healthz",
    "/readyz",
    "/metrics",
    # Static file endpoints
    "/static/",
    "/assets/",
    "/favicon.ico",
    "/logo192.png",
    "/vite.svg",
    "/manifest.json",
]

uvicorn_logger = logging.getLogger("uvicorn.access")
for path in paths_to_filter:
    # Add a filter for each path to exclude it from the logs
    uvicorn_logger.addFilter(EndpointFilter(path=path))
