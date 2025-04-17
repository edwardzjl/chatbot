import logging

from .base import LLMProvider
from .llamacpp import llamacppProvider
from .tgi import TGIProvider
from .vllm import VLLMProvider
from .utils import guess_provider


logger = logging.getLogger(__name__)


async def llm_provider_factory(
    base_url: str, provider_name: str | None = None
) -> LLMProvider:
    if not provider_name:
        return await guess_provider(base_url)

    match provider_name.lower():
        case "vllm":
            return VLLMProvider(base_url)
        case "tgi":
            return TGIProvider(base_url)
        case "llamacpp":
            return llamacppProvider(base_url)
        case _:
            logger.warning(
                "Unknown provider %s, guessing from server features", provider_name
            )
            return await guess_provider(base_url)


__all__ = [
    "LLMProvider",
    "guess_provider",
    "llm_provider_factory",
]
