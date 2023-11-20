from contextvars import ContextVar

session_id = ContextVar("session_id", default=None)
