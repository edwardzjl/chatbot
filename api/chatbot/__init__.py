import logging
import os
import sys

from loguru import logger

from chatbot.main import app

__all__ = ["app"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger.remove()
logger.add(sys.stdout, level=LOG_LEVEL)


class EndpointFilter(logging.Filter):
    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1


uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/api/healthz"))
uvicorn_logger.addFilter(EndpointFilter(path="/api/openapi.json"))
uvicorn_logger.addFilter(EndpointFilter(path="/api/docs"))
uvicorn_logger.addFilter(EndpointFilter(path="/api/redoc"))
