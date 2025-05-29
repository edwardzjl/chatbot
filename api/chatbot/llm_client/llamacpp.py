from functools import cache
from typing import override
from urllib.parse import urljoin

from langchain_core.messages import BaseMessage, convert_to_openai_messages

from .base import ReasoningChatOpenai


class llamacppReasoningChatOpenai(ReasoningChatOpenai):
    # Note on caching:
    # Using @functools.cache/@lru_cache on methods can prevent instance GC.
    # See <https://rednafi.com/python/lru_cache_on_methods/> for details.
    # This is acceptable here as client instances (one per LLM) live for the app's lifespan.
    # Standard functools caches do not support async methods.
    # Since I want to apply caching here, async is not used for this method.
    @cache
    def get_context_length(self) -> int:
        http_client = self.http_client or self.root_client._client
        resp = http_client.get(urljoin(self.openai_api_base, "/props"))
        props = resp.json()
        return props["default_generation_settings"]["n_ctx"]

    @override
    def get_num_tokens_from_messages(
        self, messages: list[BaseMessage], **kwargs
    ) -> int:
        # Use `list` to create a copy of the messages to avoid modifying the original list
        messages = list(messages)
        for message in messages:
            self.patch_content(message)

        http_client = self.http_client or self.root_client._client
        resp = http_client.post(
            urljoin(self.openai_api_base, "/apply-template"),
            json={
                "messages": convert_to_openai_messages(messages),
            },
        )
        data = resp.json()

        resp = http_client.post(
            urljoin(self.openai_api_base, "/tokenize"),
            json={
                "content": data["prompt"],
            },
        )
        data = resp.json()
        return len(data["tokens"])

    def __hash__(self):
        # I use cache on `self` and cache doesn't work with mutable objects.
        return self.model_dump_json().__hash__()
