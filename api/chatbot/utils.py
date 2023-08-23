from datetime import datetime, timezone


def utcnow():
    """
    datetime.datetime.utcnow() does not contain timezone information.
    """
    return datetime.now(timezone.utc)
