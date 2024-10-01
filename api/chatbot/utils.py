import re
from datetime import datetime, timezone


def utcnow():
    """
    datetime.datetime.utcnow() does not contain timezone information.
    """
    return datetime.now(timezone.utc)


def remove_driver(dsn: str) -> str:
    """Remove the 'driver' part from a connection string, if one is present in the URI scheme.

    ORM libraries like SQLAlchemy require the driver part for non-default drivers.
    For example, SQLAlchemy defaults to psycopg2 for PostgreSQL, so one need to specify
    'postgresql+psycopg' as the scheme for using psycopg3.

    In contrast, psycopg3 itself only accepts the URL scheme supported by PostgreSQL, which is 'postgresql'.

    Args:
        dsn (str): The original connection string.

    Returns:
        str: Connection string with the driver part removed.
    """
    pattern = r"\+psycopg"
    return re.sub(pattern, "", dsn)
