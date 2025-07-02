import logging

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from sqlalchemy.exc import NoResultFound


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(NoResultFound, not_found_error_handler)
    app.add_exception_handler(Exception, exception_handler)


def not_found_error_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )


def exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.exception("Unhandled error during request %s", request)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "server error"},
    )
