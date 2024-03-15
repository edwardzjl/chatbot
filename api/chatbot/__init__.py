import logging
import sys

from loguru import logger

from chatbot.config import settings
from chatbot.main import app

__all__ = ["app"]

logger.remove()
logger.add(sys.stdout, level=settings.log_level)


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
