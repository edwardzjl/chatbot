from typing import Any, Optional

from langchain.memory import VectorStoreRetrieverMemory
from langchain_core.documents import Document
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    get_buffer_string,
)
from loguru import logger


class ConversationRetrieverMemory(VectorStoreRetrieverMemory):
    return_messages: bool = True
    """Conversation memory should prefer to return messages instead of string."""
    output_key: str
    """Must specify output_key to form messages from documents."""

    def load_memory_variables(
        self, inputs: dict[str, Any]
    ) -> dict[str, list[BaseMessage] | str]:
        """Return similar messages in chat history."""
        if self.return_docs:
            logger.warning(
                "`return_docs` has no effect in `ConversationRetrieverMemory`, please use `return_messages` instead."
            )
        input_key = self._get_single_input_key(inputs)
        query = inputs[input_key]
        try:
            docs = self.retriever.get_relevant_documents(query)
            logger.debug(f"loaded {len(docs)} documents from memory")
        except Exception as e:
            # probably no documents found
            logger.debug(f"error loading memory variables: {e}")
            docs = []
        messages = []
        for doc in docs:
            messages.append(HumanMessage(content=doc.metadata[input_key]))
            messages.append(AIMessage(content=doc.metadata[self.output_key]))
        if not self.return_messages:
            result = get_buffer_string(messages)
        else:
            result = messages
        return {self.memory_key: result}

    def _form_documents(
        self, inputs: dict[str, Any], outputs: dict[str, str]
    ) -> list[Document]:
        """Format context from this conversation to buffer."""
        # Each document should only include the current turn, not the chat history
        exclude = set(self.exclude_input_keys)
        exclude.add(self.memory_key)
        filtered_inputs = {k: v for k, v in inputs.items() if k not in exclude}
        texts = [
            f"{k}: {v}"
            for k, v in list(filtered_inputs.items()) + list(outputs.items())
        ]
        # TODO: I don't know whether I should keep the page_content as it is, or simply combine input and output
        # As chat memory seems to have a limit form of single input and single output.
        # But maybe keep as it is provides more flexibility in the future.
        page_content = "\n".join(texts)
        input_key = self._get_single_input_key(inputs)
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        return [
            Document(
                page_content=page_content,
                metadata={
                    input_key: inputs[input_key],
                    output_key: outputs[output_key],
                },
            )
        ]

    def _get_single_input_key(self, inputs: dict[str, Any]) -> str:
        if self.input_key is None:
            return self._get_prompt_input_key(inputs, self.memory_variables)
        else:
            return self.input_key
