from __future__ import annotations

from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from chatbot.llm.client import ReasoningChatOpenai


class S3Settings(BaseModel):
    endpoint: str = "play.min.io"
    access_key: str | None = None
    secret_key: str | None = None
    secure: bool = True
    bucket: str = "chatbot"  # TODO: this default value is for easy testing


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    llm: ChatOpenAI
    safety_llm: ChatOpenAI | None = None

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

    @field_validator("llm", mode="before")
    @classmethod
    def construct_openai_client(cls, value: Any) -> ChatOpenAI:
        if not isinstance(value, dict):
            return value
        return ReasoningChatOpenai(**value)

    @field_validator("safety_llm", mode="before")
    @classmethod
    def construct_safety_openai_client(cls, value: Any) -> ChatOpenAI | None:
        if not value:
            return None
        if not isinstance(value, dict):
            return value
        return ChatOpenAI(**value, tags=["internal"])

    @model_validator(mode="after")
    def set_default_standby_url(self) -> Self:
        if self.db_standby_url is None:
            self.db_standby_url = self.db_primary_url
        return self

    def __hash__(self):
        # LRU cache doesn't work with mutable objects, so we need to hash the settings object
        return self.model_dump_json().__hash__()
