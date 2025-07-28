from functools import cache
from typing import Any, override
from urllib.parse import urljoin

from httpx import Client
from langchain_core.messages import BaseMessage

from .base import ExtendedChatOpenAI


class TGIChatOpenAI(ExtendedChatOpenAI):
    server_info: dict[str, Any] | None = None

    # Note on caching:
    # Using `@functools.cache` or `@functools.lru_cache` on methods can prevent instance GC.
    # See <https://rednafi.com/python/lru_cache_on_methods/> for details.
    # This is acceptable here as client instances (one per LLM) live for the app's lifespan.
    # Also note that standard functools caches do not support async methods.
    # Since I want to apply caching here, async is not used for this method.
    @cache
    def get_context_length(self) -> int:
        if self.server_info is None:
            self._fetch_server_info()

        max_model_len = self.server_info.get("max_total_tokens")

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

        url = urljoin(self.openai_api_base, "/chat_tokenize")
        http_client: Client = self.http_client or self.root_client._client
        resp = http_client.post(
            url,
            json={"model": self.model_name, "messages": oai_messages},
        ).raise_for_status()
        data = resp.json()
        return len(data["tokenize_response"])

    def _fetch_server_info(self) -> None:
        """Fetches server information."""
        http_client: Client = self.http_client or self.root_client._client
        resp = http_client.get(
            urljoin(self.openai_api_base, "/info")
        ).raise_for_status()
        self.server_info = resp.json()

    def __hash__(self):
        # I use cache on `self` and cache doesn't work with mutable objects.
        return self.model_dump_json().__hash__()
