from __future__ import annotations

from functools import partial
from typing import Callable, override
from urllib.parse import urljoin

from aiohttp import ClientTimeout, ClientResponseError
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend
from langchain_core.messages.utils import convert_to_openai_messages
from requests.exceptions import HTTPError, Timeout
from requests_cache import CachedSession
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from .base import LLMProvider


class llamacppProvider(LLMProvider):
    """
    See <https://github.com/ggml-org/llama.cpp/blob/master/examples/server/README.md>
    """

    def __init__(self, base_url: str, timeout: int | None = 5):
        # aiohttp requires base_url to end with a slash
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.timeout = timeout
        self.session = CachedSession(
            "llm.provider.llamacpp.cache",
            expire_after=-1,
            ignored_parameters=["api_key"],
        )
        # Monkey patch the session to add a global 5 seconds timeout
        # See <https://requests.readthedocs.io/en/latest/user/advanced/#timeouts>
        if self.timeout:
            self.session.request = partial(self.session.request, timeout=self.timeout)

    @retry(
        retry=retry_if_exception_type((ClientResponseError, TimeoutError)),
        stop=stop_after_attempt(3),
    )
    @override
    async def get_max_tokens(self, model_name: str) -> int:
        timeout = ClientTimeout(total=self.timeout)
        async with AsyncCachedSession(
            base_url=self.base_url,
            timeout=timeout,
            raise_for_status=True,
            cache=SQLiteBackend("llm.provider.llamacpp.async.cache"),
        ) as session:
            async with await session.get("/props") as response:
                props: dict = await response.json()
        return props["default_generation_settings"]["n_ctx"]

    @override
    def get_token_counter(self, model_name: str) -> Callable[[list], int] | None:
        return partial(self.token_counter_lc, model_name)

    # NOTE: this function is used as the `token_counter` parameter of langchain's `langchain_core.messages.utils.trim_messages` function.
    # So it must be a synchronous function.
    @retry(
        retry=retry_if_exception_type((HTTPError, Timeout)), stop=stop_after_attempt(3)
    )
    def token_counter_lc(self, model_name: str, messages: list) -> int:
        """Get the number of tokens for a list of messages.

        Args:
            model_name (str): The name or ID of the model.
            messages (list): A list of messages to tokenize.

        Returns:
            int: The number of tokens in the provided messages.
        """
        prompt_resp = self.session.post(
            urljoin(self.base_url, "/apply-template"),
            json={
                "messages": convert_to_openai_messages(messages),
            },
        )
        prompt_resp.raise_for_status()
        prompt = prompt_resp.json()["prompt"]
        token_resp = self.session.post(
            urljoin(self.base_url, "/tokenize"),
            json={
                "content": prompt,
            },
        )
        token_resp.raise_for_status()
        return len(token_resp.json()["tokens"])

    def __del__(self):
        """cleanup"""
        self.session.close()
