from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


class S3Settings(BaseModel):
    endpoint: str = "play.min.io"
    access_key: str | None = None
    secret_key: str | None = None
    secure: bool = True
    bucket: str = "chatbot"  # TODO: this default value is for easy testing


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    llm: dict[str, Any] = Field(default_factory=lambda: {"api_key": "NOT_SET"})
    safety_llm: dict[str, Any] | None = None
    db_primary_url: PostgresDsn | str = "sqlite+aiosqlite:///chatbot.sqlite"
    """Primary database url for read / write connections."""
    db_standby_url: PostgresDsn | str | None = None
    """Standby database url for read only connections.
    Defaults to `postgres_primary_url`.
    """

    s3: S3Settings = Field(default_factory=S3Settings)

    serp_api_key: str | None = None
    ipgeolocation_api_key: str | None = None
    openmeteo_api_key: str | None = None

    @model_validator(mode="after")
    def set_default_standby_url(self) -> Self:
        if self.db_standby_url is None:
            self.db_standby_url = self.db_primary_url
        return self


settings = Settings()
