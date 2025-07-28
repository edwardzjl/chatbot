import logging
from urllib.parse import urljoin

import requests
from requests.exceptions import HTTPError

from .base import ExtendedChatOpenAI
from .github import GithubChatOpenAI
from .llamacpp import llamacppChatOpenAI
from .tgi import TGIChatOpenAI
from .vllm import VLLMChatOpenAI


logger = logging.getLogger(__name__)


def llm_client_factory(
    base_url: str,
    provider_name: str | None = None,
    **client_kwargs,
) -> ExtendedChatOpenAI:
    """Factory function to create the appropriate LLM client instance.

    Args:
        base_url: The base URL of the LLM provider
        provider_name: Optional provider name hint
        **client_kwargs: Additional arguments to pass to the client constructor

    Returns:
        An instance of the appropriate LLM client
    """
    # Try to get client type from known provider names first
    if provider_name and (client_type := _get_client_type_by_name(provider_name)):
        return client_type(base_url=base_url, **client_kwargs)

    # Fall back to guessing the provider from server features
    return _create_client_from_guess(base_url, provider_name, **client_kwargs)


def _get_client_type_by_name(provider_name: str) -> type[ExtendedChatOpenAI] | None:
    """Get client type by provider name, return None if unknown."""
    match provider_name.lower():
        case "github":
            return GithubChatOpenAI
        case "vllm":
            return VLLMChatOpenAI
        case "tgi":
            return TGIChatOpenAI
        case "llamacpp":
            return llamacppChatOpenAI
        case _:
            return None


def _create_client_from_guess(
    base_url: str, provider_name: str | None = None, **client_kwargs
) -> ExtendedChatOpenAI:
    """Create client by guessing provider type and pre-populate cache if possible."""
    if provider_name:
        logger.warning(
            "Unknown provider %s, guessing from server features", provider_name
        )

    return guess_provider(base_url, **client_kwargs)


# This should not be used often and I am using it in an pydantic model validator
# to instantiate all clients, so no async
def guess_provider(base_url: str, **client_kwargs) -> ExtendedChatOpenAI:
    """Guess the provider type by checking available endpoints and return a client instance.

    Args:
        base_url: The base URL of the LLM provider
        **client_kwargs: Additional arguments to pass to the client constructor

    Returns:
        An instance of the appropriate LLM client with pre-populated cache
    """
    try:
        resp = requests.get(urljoin(base_url, "/info"))
        resp.raise_for_status()
        data = resp.json()
        logger.info("Provider has `/info` endpoint, assuming it's TGI")
        return TGIChatOpenAI(base_url=base_url, server_info=data, **client_kwargs)
    except HTTPError:
        pass

    try:
        resp = requests.get(urljoin(base_url, "/catalog/models"))
        resp.raise_for_status()
        data = resp.json()
        logger.info("Provider has `/catalog/models` endpoint, assuming it's github")
        models_meta = {model["id"]: model for model in data}
        return GithubChatOpenAI(
            base_url=base_url, models_meta=models_meta, **client_kwargs
        )
    except HTTPError:
        pass

    try:
        resp = requests.get(urljoin(base_url, "/get_server_info"))
        resp.raise_for_status()
        data = resp.json()
        logger.info("Provider has `/get_server_info` endpoint, assuming it's SGLang")
        # TODO: implement SGLang provider
        return ExtendedChatOpenAI(base_url=base_url, **client_kwargs)
    except HTTPError:
        pass

    try:
        resp = requests.get(urljoin(base_url, "/props"))
        resp.raise_for_status()
        data = resp.json()
        logger.info("Provider has `/props` endpoint, assuming it's llamacpp")
        return llamacppChatOpenAI(base_url=base_url, server_props=data, **client_kwargs)
    except HTTPError:
        pass

    resp = requests.get(urljoin(base_url, "/v1/models"))
    resp.raise_for_status()
    data = resp.json()
    models = data.get("data", [])

    assert models

    match models[0]["owned_by"].lower():
        case "vllm":
            models_meta = {model["id"]: model for model in models}
            return VLLMChatOpenAI(
                base_url=base_url, models_meta=models_meta, **client_kwargs
            )
        case _:
            logger.warning(
                "Unknown provider %s, falling back to Default client",
                models[0]["owned_by"],
            )
            return ExtendedChatOpenAI(base_url=base_url, **client_kwargs)
