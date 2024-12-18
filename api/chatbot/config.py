from __future__ import annotations

import re
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    PositiveInt,
    PostgresDsn,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


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


class EmbeddingSettings(BaseModel):
    url: HttpUrl
    dims: PositiveInt


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    llm: dict[str, Any] = Field(default_factory=lambda: {"api_key": "NOT_SET"})
    safety_llm: dict[str, Any] | None = None
    embeddings: EmbeddingSettings | None = None
    postgres_primary_url: PostgresDsn = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/"
    )
    """Primary database url. Read/Write. Must be a valid postgresql connection string."""
    postgres_standby_url: PostgresDsn | None = None
    """Standby database url. Read Only. If present must be a valid postgresql connection string.
    Defaults to `postgres_primary_url`.
    """

    @model_validator(mode="after")
    def set_default_standby_url(self) -> Self:
        if self.postgres_standby_url is None:
            self.postgres_standby_url = self.postgres_primary_url
        return self

    @property
    def psycopg_primary_url(self) -> str:
        return remove_postgresql_variants(str(self.postgres_primary_url))

    @property
    def psycopg_standby_url(self) -> str:
        return remove_postgresql_variants(str(self.postgres_standby_url))


settings = Settings()
