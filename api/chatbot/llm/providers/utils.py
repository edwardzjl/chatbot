import logging

from aiohttp import ClientResponseError
from aiohttp_client_cache import CachedSession as AsyncCachedSession, SQLiteBackend

from .base import LLMProvider, UnknownLLMProvider
from .tgi import TGIProvider
from .vllm import VLLMProvider
from .llamacpp import llamacppProvider


logger = logging.getLogger(__name__)


async def guess_provider(base_url: str) -> LLMProvider:
    # aiohttp requires base_url to end with a slash
    base_url = base_url if base_url.endswith("/") else base_url + "/"
    async with AsyncCachedSession(
        base_url=base_url,
        raise_for_status=True,
        cache=SQLiteBackend("llm.provider.async.cache"),
    ) as session:
        try:
            async with await session.get("/info") as response:
                # TGI, see <https://huggingface.github.io/text-generation-inference/>
                await response.json()
                logger.info("Provider has `/info` endpoint, assuming it's TGI")
                return TGIProvider(base_url)
        except ClientResponseError as e:
            if e.status != 404:
                logger.exception("Error while trying to guess provider")
                raise
        try:
            async with await session.get("/get_server_info") as response:
                # SGLang, see <https://docs.sglang.ai/backend/native_api.html>
                await response.json()
                logger.info(
                    "Provider has `/get_server_info` endpoint, assuming it's SGLang"
                )
                # TODO: implement SGLang provider
        except ClientResponseError as e:
            if e.status != 404:
                logger.exception("Error while trying to guess provider")
                raise
        async with await session.get("/v1/models") as response:
            data: dict = await response.json()
            models = data.get("data", [])

            assert models

            match models[0]["owned_by"].lower():
                case "vllm":
                    return VLLMProvider(base_url)
                case "llama-cpp":
                    return llamacppProvider(base_url)
                case _:
                    logger.warning(
                        "Unknown provider %s, falling back to UnknownLLMProvider",
                        models[0]["owned_by"],
                    )
                    return UnknownLLMProvider()
