import logging
from functools import partial
from typing import Any, Callable, override
from urllib.parse import urljoin

from langchain_core.messages.utils import convert_to_openai_messages

from chatbot.http_client import HttpClient

from .base import LLMProvider


logger = logging.getLogger(__name__)


class TGIProvider(LLMProvider):
    """
    See <https://huggingface.github.io/text-generation-inference/>
    """

    def __init__(self, base_url: str, http_client: HttpClient | None = None):
        self.base_url = base_url
        self.client = http_client or HttpClient()

    async def get_model_info(self) -> dict[str, Any]:
        async with await self.client.aget(urljoin(self.base_url, "/info")) as resp:
            return await resp.json()

    @override
    async def get_max_tokens(self, model_name: str) -> int:
        model_info = await self.get_model_info()
        return model_info.get("max_total_tokens")

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
        url = urljoin(self.base_url, "/chat_tokenize")
        # use 'prompt' param instead of 'messages' to get the number of tokens in the prompt
        resp = self.client.post(
            url,
            json={
                "model": model_name,
                "messages": convert_to_openai_messages(messages),
            },
        )
        data = resp.json()
        return len(data["tokenize_response"])
