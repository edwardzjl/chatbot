from __future__ import annotations

from functools import partial
from typing import Callable, override
from urllib.parse import urljoin

from langchain_core.messages.utils import convert_to_openai_messages

from chatbot.http_client import HttpClient

from .base import LLMProvider


class llamacppProvider(LLMProvider):
    """
    See <https://github.com/ggml-org/llama.cpp/blob/master/examples/server/README.md>
    """

    def __init__(self, base_url: str, http_client: HttpClient | None = None):
        self.base_url = base_url
        self.client = http_client or HttpClient()

    @override
    async def get_max_tokens(self, model_name: str) -> int:
        async with await self.client.aget(urljoin(self.base_url, "/props")) as resp:
            props = await resp.json()
        return props["default_generation_settings"]["n_ctx"]

    @override
    def get_token_counter(self, model_name: str) -> Callable[[list], int] | None:
        return partial(self.token_counter_lc, model_name)

    # NOTE: this function is used as the `token_counter` parameter of langchain's `langchain_core.messages.utils.trim_messages` function.
    # So it must be a synchronous function.
    def token_counter_lc(self, model_name: str, messages: list) -> int:
        """Get the number of tokens for a list of messages.

        Args:
            model_name (str): The name or ID of the model.
            messages (list): A list of messages to tokenize.

        Returns:
            int: The number of tokens in the provided messages.
        """
        resp = self.client.post(
            urljoin(self.base_url, "/apply-template"),
            json={
                "messages": convert_to_openai_messages(messages),
            },
        )
        prompt = resp.json()

        tokens = self.client.post(
            urljoin(self.base_url, "/tokenize"),
            json={
                "content": prompt["prompt"],
            },
        )
        return len(tokens["tokens"])
