import logging

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(NoResultFound, handle_no_result_found)
    app.add_exception_handler(IntegrityError, handle_integrity_error)
    app.add_exception_handler(ValueError, handle_value_error)
    app.add_exception_handler(PermissionError, handle_permission_error)
    app.add_exception_handler(ConnectionError, handle_connection_error)
    app.add_exception_handler(Exception, handle_generic_exception)


def handle_no_result_found(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Resource not found", "detail": str(exc)},
    )


def handle_integrity_error(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": "Resource already exists", "detail": str(exc)},
    )


def handle_value_error(request: Request, exc: ValueError):
    logger.exception("Unhandled ValueError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "Invalid input", "detail": str(exc)},
    )


def handle_permission_error(request: Request, exc: PermissionError):
    logger.exception("Unhandled PermissionError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"message": "Permission denied", "detail": str(exc)},
    )


def handle_connection_error(request: Request, exc: ConnectionError):
    logger.exception("Unhandled ConnectionError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"message": "Service unavailable", "detail": str(exc)},
    )


def handle_generic_exception(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        # Do not expose error details
        content={"message": "Server error"},
    )
