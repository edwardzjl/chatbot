import logging
from typing import Type
from urllib.parse import urljoin

import requests
from requests.exceptions import HTTPError

from .base import ExtendedChatOpenAI
from .llamacpp import llamacppChatOpenAI
from .tgi import TGIChatOpenAI
from .vllm import VLLMChatOpenAI


logger = logging.getLogger(__name__)


def llm_client_type_factory(
    base_url: str,
    provider_name: str | None = None,
) -> Type[ExtendedChatOpenAI]:
    if not provider_name:
        return guess_provider(base_url)

    match provider_name.lower():
        case "vllm":
            return VLLMChatOpenAI
        case "tgi":
            return TGIChatOpenAI
        case "llamacpp":
            return llamacppChatOpenAI
        case _:
            logger.warning(
                "Unknown provider %s, guessing from server features", provider_name
            )
            return guess_provider(base_url)


# This should not be used often and I am using it in an pydantic model validator
# to instantiate all clients, so no async
def guess_provider(base_url: str) -> Type[ExtendedChatOpenAI]:
    try:
        resp = requests.get(urljoin(base_url, "/info"))
        resp.raise_for_status()
        resp.json()
        logger.info("Provider has `/info` endpoint, assuming it's TGI")
        return TGIChatOpenAI
    except HTTPError:
        pass

    try:
        resp = requests.get(urljoin(base_url, "/get_server_info"))
        resp.raise_for_status()
        resp.json()
        logger.info("Provider has `/get_server_info` endpoint, assuming it's SGLang")
        # TODO: implement SGLang provider
        return ExtendedChatOpenAI
    except HTTPError:
        pass

    resp = requests.get(urljoin(base_url, "/v1/models"))
    resp.raise_for_status()
    data = resp.json()
    models = data.get("data", [])

    assert models

    match models[0]["owned_by"].lower():
        case "vllm":
            return VLLMChatOpenAI
        case "llama-cpp":
            return llamacppChatOpenAI
        case _:
            logger.warning(
                "Unknown provider %s, falling back to Default client",
                models[0]["owned_by"],
            )
            return ExtendedChatOpenAI
