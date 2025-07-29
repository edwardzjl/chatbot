import logging
from functools import cache
from typing import Any, Callable, Sequence, override
from urllib.parse import urljoin

from httpx import Client
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langchain_openai.chat_models.base import _count_image_tokens, _url_to_size

from .base import ExtendedChatOpenAI


logger = logging.getLogger(__name__)


class GithubChatOpenAI(ExtendedChatOpenAI):
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

        model_limits = model_info.get("limits")
        # Should not happen, for type hint only.
        assert model_limits is not None, (
            f"Model {self.model_name} does not have `limits`."
        )

        return model_limits.get("max_input_tokens") + model_limits.get(
            "max_output_tokens"
        )

    @override
    def get_num_tokens_from_messages(
        self,
        messages: list[BaseMessage],
        tools: Sequence[dict[str, Any] | type | Callable | BaseTool] | None = None,
    ) -> int:
        """Adjusted from `langchain_openai.chat_models.BaseChatOpenAI.get_num_tokens_from_messages`."""
        # TODO: Count bound tools as part of input.
        if tools is not None:
            logger.warning(
                "Counting tokens in tool schemas is not yet supported. Ignoring tools."
            )

        model, encoding = self._get_encoding_model()
        # github only has openai/gpt4+, no more gpt-3.5-*
        if model.startswith("openai/gpt-4"):
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"get_num_tokens_from_messages() is not presently implemented "
                f"for model {model}. See "
                "https://platform.openai.com/docs/guides/text-generation/managing-tokens"  # noqa: E501
                " for information on how messages are converted to tokens."
            )
        num_tokens = 0
        oai_messages = self.convert_messages(messages)
        for message in oai_messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                # This is an inferred approximation. OpenAI does not document how to
                # count tool message tokens.
                if key == "tool_call_id":
                    num_tokens += 3
                    continue
                if isinstance(value, list):
                    # content or tool calls
                    for val in value:
                        if isinstance(val, str) or val["type"] == "text":
                            text = val["text"] if isinstance(val, dict) else val
                            num_tokens += len(encoding.encode(text))
                        elif val["type"] == "image_url":
                            if val["image_url"].get("detail") == "low":
                                num_tokens += 85
                            else:
                                image_size = _url_to_size(val["image_url"]["url"])
                                if not image_size:
                                    continue
                                num_tokens += _count_image_tokens(*image_size)
                        # Tool/function call token counting is not documented by OpenAI.
                        # This is an approximation.
                        elif val["type"] == "function":
                            num_tokens += len(
                                encoding.encode(val["function"]["arguments"])
                            )
                            num_tokens += len(encoding.encode(val["function"]["name"]))
                        elif val["type"] == "file":
                            logger.warning(
                                "Token counts for file inputs are not supported. "
                                "Ignoring file inputs."
                            )
                            pass
                        else:
                            raise ValueError(
                                f"Unrecognized content block type\n\n{val}"
                            )
                elif not value:
                    continue
                else:
                    # Cast str(value) in case the message value is not a string
                    # This occurs with function messages
                    num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        # every reply is primed with <im_start>assistant
        num_tokens += 3
        return num_tokens

    def _fetch_models_meta(self) -> None:
        http_client: Client = self.http_client or self.root_client._client
        resp = http_client.get(
            urljoin(self.openai_api_base, "/catalog/models")
        ).raise_for_status()
        data = resp.json()
        self.models_meta = {model["id"]: model for model in data}

    def __hash__(self):
        # I use cache on `self` and cache doesn't work with mutable objects.
        return self.model_dump_json().__hash__()
