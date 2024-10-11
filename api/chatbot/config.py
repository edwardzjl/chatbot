import re
from typing import Any

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def remove_postgresql_variants(dsn: str) -> str:
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
    pattern = r"postgresql\+psycopg(?:2(?:cffi)?)?"

    return re.sub(pattern, "postgresql", dsn)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    llm: dict[str, Any] = Field(default_factory=lambda: {"api_key": "NOT_SET"})
    db_url: PostgresDsn = "postgresql+psycopg://postgres:postgres@localhost:5432/"
    """Database url. Must be a valid postgresql connection string."""

    @property
    def psycopg_url(self) -> str:
        return remove_postgresql_variants(str(self.db_url))


settings = Settings()
