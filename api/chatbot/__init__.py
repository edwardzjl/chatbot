import sys

from loguru import logger

from chatbot.config import settings
from chatbot.main import app

__all__ = ["app"]

logger.remove()
logger.add(sys.stdout, level=settings.log_level)
