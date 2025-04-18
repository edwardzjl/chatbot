import logging

from aiohttp import ClientResponseError

from chatbot.http_client import HttpClient

from .base import LLMProvider, UnknownLLMProvider
from .tgi import TGIProvider
from .vllm import VLLMProvider
from .llamacpp import llamacppProvider


logger = logging.getLogger(__name__)


async def guess_provider(
    base_url: str, http_client: HttpClient | None = None
) -> LLMProvider:
    http_client = http_client or HttpClient()
    try:
        await http_client.aget("/info")
        logger.info("Provider has `/info` endpoint, assuming it's TGI")
        return TGIProvider(base_url, http_client)
    except ClientResponseError as e:
        if e.status != 404:
            logger.exception("Error while trying to guess provider")
            raise
    try:
        await http_client.aget("/get_server_info")
        logger.info("Provider has `/get_server_info` endpoint, assuming it's SGLang")
        # TODO: implement SGLang provider
        return UnknownLLMProvider()
    except ClientResponseError as e:
        if e.status != 404:
            logger.exception("Error while trying to guess provider")
            raise
    data = await http_client.aget("/v1/models")
    models = data.get("data", [])

    assert models

    match models[0]["owned_by"].lower():
        case "vllm":
            return VLLMProvider(base_url, http_client)
        case "llama-cpp":
            return llamacppProvider(base_url, http_client)
        case _:
            logger.warning(
                "Unknown provider %s, falling back to UnknownLLMProvider",
                models[0]["owned_by"],
            )
            return UnknownLLMProvider()
