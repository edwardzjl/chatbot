from typing import Optional, Sequence

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    FunctionMessage,
    ChatMessage,
)


class FlexConversationBufferWindowMemory(ConversationBufferWindowMemory):
    """A flexible conversation memory with customizable message suffix and prefix delimiter."""

    human_suffix: Optional[str] = None
    ai_suffix: Optional[str] = None
    prefix_delimiter: str = ": "

    @property
    def buffer_as_str(self) -> str:
        """Exposes the buffer as a string in case return_messages is True."""
        messages = self.chat_memory.messages[-self.k * 2 :] if self.k > 0 else []
        return self.get_buffer_string(messages)

    def get_buffer_string(
        self,
        messages: Sequence[BaseMessage],
    ) -> str:
        string_messages = []
        for m in messages:
            if isinstance(m, HumanMessage):
                role = self.human_prefix
                suffix = self.human_suffix
            elif isinstance(m, AIMessage):
                role = self.ai_prefix
                suffix = self.ai_suffix
            elif isinstance(m, SystemMessage):
                role = "System"
            elif isinstance(m, FunctionMessage):
                role = "Function"
            elif isinstance(m, ChatMessage):
                role = m.role
            else:
                raise ValueError(f"Got unsupported message type: {m}")
            message = (
                f"{role}{self.prefix_delimiter}{m.content}{suffix if suffix else ''}"
            )
            if isinstance(m, AIMessage) and "function_call" in m.additional_kwargs:
                message += f"{m.additional_kwargs['function_call']}"
            string_messages.append(message)

        return "\n".join(string_messages)
