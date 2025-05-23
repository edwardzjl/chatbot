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


uvicorn_logger = logging.getLogger("uvicorn.access")
# API doc endpoints
uvicorn_logger.addFilter(EndpointFilter(path="/api/openapi.json"))
uvicorn_logger.addFilter(EndpointFilter(path="/api/docs"))
uvicorn_logger.addFilter(EndpointFilter(path="/api/redoc"))
# Health and metrics endpoints
uvicorn_logger.addFilter(EndpointFilter(path="/api/healthz"))
uvicorn_logger.addFilter(EndpointFilter(path="/metrics"))
# Static file endpoints
## CRA build files
uvicorn_logger.addFilter(EndpointFilter(path="/static/"))
uvicorn_logger.addFilter(EndpointFilter(path="/favicon.ico"))
uvicorn_logger.addFilter(EndpointFilter(path="/logo192.png"))
uvicorn_logger.addFilter(EndpointFilter(path="/manifest.json"))
## Vite build files
uvicorn_logger.addFilter(EndpointFilter(path="/assets/"))
uvicorn_logger.addFilter(EndpointFilter(path="/vite.svg"))
