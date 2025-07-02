from __future__ import annotations

import logging
from typing import Any, Self

from langchain_openai import ChatOpenAI
from pydantic import (
    BaseModel,
    Field,
    PostgresDsn,
    UrlConstraints,
    field_validator,
    model_validator,
)
from pydantic.networks import _BaseMultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from chatbot.llm_client import ReasoningChatOpenai, llm_client_type_factory
from chatbot.llm_client.base import StreamThinkingProcessor


logger = logging.getLogger(__name__)


class SQLiteDsn(_BaseMultiHostUrl):
    _constraints = UrlConstraints(
        host_required=False,
        allowed_schemes=[
            "sqlite",
            "sqlite+pysqlite",
            "sqlite+aiosqlite",
            "sqlite+pysqlcipher",
        ],
    )


class S3Settings(BaseModel):
    endpoint: str = "play.min.io"
    access_key: str | None = None
    secret_key: str | None = None
    secure: bool = True
    bucket: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    llms: list[ChatOpenAI]
    safety_llm: ChatOpenAI | None = None

    db_primary_url: PostgresDsn | SQLiteDsn = "sqlite+aiosqlite:///chatbot.sqlite"
    """Primary database url for read / write connections."""
    db_standby_url: PostgresDsn | SQLiteDsn | None = None
    """Standby database url for read only connections.
    Defaults to `db_primary_url`.
    """

    s3: S3Settings = Field(default_factory=S3Settings)

    serp_api_key: str | None = None
    ipgeolocation_api_key: str | None = None
    openmeteo_api_key: str | None = None

    @field_validator("llms", mode="before")
    @classmethod
    def construct_openai_clients(cls, value: Any) -> list[ChatOpenAI]:
        if not isinstance(value, list):
            logger.info("llms configuration is not a list, converting to list.")
            value = [value]

        clients = []
        for item in value:
            if isinstance(item, dict):
                # THIS IS STUPID!
                # `langchain_openai.chat_models.base.BaseChatOpenAI.extra_body` is typed as `Optional[Mapping[str, Any]]`.
                # Pydantic does not automatically convert the *values* within this mapping.
                # Since environment variables are always strings, this results in string values in `extra_body`, e.g.:
                # {"repetition_penalty": "1.05", "chat_template_kwargs": {"enable_thinking": "True"}}
                # Crucially, vLLM's "non-thinking mode" requires `extra_body['chat_template_kwargs']['enable_thinking']` to be the *boolean* `False`, not the string "False".
                # IDK whether other parameters in `extra_body` also require specific types, but converting them proactively is a safe approach.
                processed = {
                    key: preprocess_value(val) if key == "extra_body" else val
                    for key, val in item.items()
                }
                thinking_processor = StreamThinkingProcessor()
                try:
                    clz = llm_client_type_factory(
                        processed["base_url"],
                        (processed.get("metadata") or {}).get("provider"),
                    )
                    clients.append(
                        clz(thinking_processor=thinking_processor, **processed)
                    )
                except:  # noqa: E722
                    logger.exception("Error guessing provider for %s", processed)
                    clients.append(
                        ReasoningChatOpenai(
                            thinking_processor=thinking_processor, **processed
                        )
                    )
            else:
                clients.append(item)
        return clients

    @field_validator("llms", mode="after")
    @classmethod
    def atleast_one_clients(cls, value: list[ChatOpenAI]) -> list[ChatOpenAI]:
        if not value:
            raise ValueError(
                "No valid llm configurations provided. Please provide at least one valid configuration."
            )
        return value

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

    def must_get_llm(self, name: str | None) -> ChatOpenAI:
        """Retrieves an LLM instance by its model name, defaulting if necessary.

        Searches for an LLM within `self.llms` whose `model_name` matches the
        provided `name`. If `name` is None, or if a matching LLM is not found
        for a given name, the method returns the first LLM in the `self.llms` list.

        Args:
            name: The `model_name` of the desired LLM. If None, the first LLM
                  in the list is returned.

        Returns:
            A `ChatOpenAI` instance. This will be the matching LLM if found,
            otherwise the first LLM in the list.

        Warning:
            Logs a warning if no name is provided or if the provided name does
            not match any LLM's model name in the list.
            Assumes `self.llms` is not empty; will raise `IndexError` if it is.
        """
        if name is None:
            logger.warning("No LLM name provided, returning the first LLM.")
            return self.llms[0]
        for llm in self.llms:
            if llm.name == name:
                return llm
        logger.warning("LLM name %s not found, returning the first LLM.", name)
        return self.llms[0]

    def __hash__(self):
        # LRU cache doesn't work with mutable objects, so we need to hash the settings object
        return self.model_dump_json().__hash__()


def preprocess_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value
    elif isinstance(value, dict):
        return {k: preprocess_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [preprocess_value(item) for item in value]
    else:
        return value
