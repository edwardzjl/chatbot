from functools import cache
from typing import Any, override
from urllib.parse import urljoin

from httpx import Client
from langchain_core.messages import BaseMessage

from .base import ExtendedChatOpenAI


class VLLMChatOpenAI(ExtendedChatOpenAI):
    models_meta: dict[str, Any] | None = None

    # Note on caching:
    # Using `@functools.cache` or `@functools.lru_cache` on methods can prevent instance GC.
    # See <https://rednafi.com/python/lru_cache_on_methods/> for details.
    # This is acceptable here as client instances (one per LLM) live for the app's lifespan.
    # Also note that standard functools caches do not support async methods.
    # Since I want to apply caching here, async is not used for this method.
    @cache
    def get_context_length(self) -> int:
        if self.models_meta is None:
            self._fetch_models_meta()

        model_info = self.models_meta.get(self.model_name)

        max_model_len = model_info.get("max_model_len")
        # Should not happen, for type hint only.
        assert max_model_len is not None, (
            f"Model {self.model_name} does not have a max_context_length."
        )
        return max_model_len

    @override
    def get_num_tokens_from_messages(
        self, messages: list[BaseMessage], **kwargs
    ) -> int:
        # Use `list` to create a copy of the messages to avoid modifying the original list
        messages = list(messages)

        oai_messages = self.convert_messages(messages)

        url = urljoin(self.openai_api_base, "/tokenize")
        http_client: Client = self.http_client or self.root_client._client
        resp = http_client.post(
            url,
            json={"model": self.model_name, "messages": oai_messages},
        ).raise_for_status()
        data = resp.json()
        return data["count"]

    def _fetch_models_meta(self) -> None:
        http_client: Client = self.http_client or self.root_client._client
        resp = http_client.get(
            urljoin(self.openai_api_base, "/v1/models")
        ).raise_for_status()
        data = resp.json()
        models = data.get("data", [])
        self.models_meta = {model["id"]: model for model in models}

    def __hash__(self):
        # I use cache on `self` and cache doesn't work with mutable objects.
        return self.model_dump_json().__hash__()
