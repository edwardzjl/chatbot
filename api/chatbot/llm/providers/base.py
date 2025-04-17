from abc import ABC, abstractmethod
from typing import Callable, override


class LLMProvider(ABC):
    @abstractmethod
    async def get_max_tokens(self, model_name: str) -> int:
        raise NotImplementedError()

    @abstractmethod
    def get_token_counter(self) -> Callable[[list], int] | None:
        raise NotImplementedError()


class UnknownLLMProvider(LLMProvider):
    @override
    async def get_max_tokens(self, model_name: str) -> int:
        raise NotImplementedError()

    @override
    def get_token_counter(self) -> Callable[[list], int] | None:
        raise NotImplementedError()
