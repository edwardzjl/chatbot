from typing import Any

from langchain_core.memory import BaseMemory
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.memory import ConversationSummaryBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from pydantic.v1 import Field


class Hippocampus(BaseChatMemory):
    """A sophiscated memory system, consists of long-term memory (retrieval) and short-term memory (buffer-window)."""

    retriever: VectorStoreRetriever = Field(exclude=True)

    """VectorStoreRetriever object to connect to."""
    long_memory_key: str = "previous_history"
    short_memory_key: str = "current_history"

    @property
    def memory_variables(self) -> list[str]:
        return [self.long_memory_key, self.short_memory_key]

    def load_memory_variables(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Return key-value pairs given the text input to the chain."""

    def save_context(self, inputs: dict[str, Any], outputs: dict[str, str]) -> None:
        """Save the context of this chain run to memory."""

    def clear(self) -> None:
        """Clear memory contents."""

    def move_to_vector_store(self):
        """Move old message to vector store."""
