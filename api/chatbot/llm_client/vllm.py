from functools import cache
from typing import Any, override
from urllib.parse import urljoin

from langchain_core.messages import BaseMessage, convert_to_openai_messages

from .base import ReasoningChatOpenai


class VLLMReasoningChatOpenai(ReasoningChatOpenai):
    # Note on caching:
    # Using @functools.cache/@lru_cache on methods can prevent instance GC.
    # See <https://rednafi.com/python/lru_cache_on_methods/> for details.
    # This is acceptable here as client instances (one per LLM) live for the app's lifespan.
    # Standard functools caches do not support async methods.
    # Since I want to apply caching here, async is not used for this method.
    @cache
    def get_models(self) -> list[dict[str, Any]]:
        http_client = self.http_client or self.root_client._client
        resp = http_client.get(urljoin(self.openai_api_base, "/v1/models"))
        data = resp.json()
        return data.get("data", [])

    # Note on caching:
    # Using @functools.cache/@lru_cache on methods can prevent instance GC.
    # See <https://rednafi.com/python/lru_cache_on_methods/> for details.
    # This is acceptable here as client instances (one per LLM) live for the app's lifespan.
    # Standard functools caches do not support async methods.
    # Since I want to apply caching here, async is not used for this method.
    @cache
    def get_context_length(self) -> int:
        models = self.get_models()
        model_info = next(
            (item for item in models if item["id"] == self.model_name), {}
        )

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

        oai_messages = convert_to_openai_messages(messages)
        zipped_messages = zip(oai_messages, messages)

        patched_messages = [
            self.patch_content(oai_message, lc_message)
            for oai_message, lc_message in zipped_messages
        ]
        _messages = self._truncate_multi_modal_contents(patched_messages)

        url = urljoin(self.openai_api_base, "/tokenize")
        http_client = self.http_client or self.root_client._client
        resp = http_client.post(
            url,
            json={"model": self.model_name, "messages": _messages},
        )
        data = resp.json()
        return data["count"]

    def __hash__(self):
        # I use cache on `self` and cache doesn't work with mutable objects.
        return self.model_dump_json().__hash__()
