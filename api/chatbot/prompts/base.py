from typing import Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.prompt_values import ChatPromptValue


class FlexPromptValue(ChatPromptValue):
    """A more flexible prompt value that wrap messages between prefix and suffix."""

    system_prefix: Optional[str] = None
    system_suffix: Optional[str] = None
    human_prefix: Optional[str] = None
    human_suffix: Optional[str] = None
    ai_prefix: Optional[str] = None
    ai_suffix: Optional[str] = None
    tool_prefix: Optional[str] = None
    tool_suffix: Optional[str] = None

    def to_string(self) -> str:
        """Return prompt as string."""
        string_messages = []
        for m in self.messages:
            prefix = self.get_prefix(m)
            suffix = self.get_suffix(m)
            message = f"{prefix}{m.content}{suffix}"
            if isinstance(m, AIMessage) and "function_call" in m.additional_kwargs:
                message += f"{m.additional_kwargs['function_call']}"
            string_messages.append(message)
        # TODO: this is a bit weird?
        # An empty message indicates that the assistant should start talking
        string_messages.append(f"{self.ai_prefix}")
        # TODO: maybe move '\n' to message suffix?
        msgs = "\n".join(string_messages)
        return msgs

    def get_prefix(self, message: BaseMessage) -> str:
        if "prefix" in message.additional_kwargs:
            # allow custom prefix
            # for example `<|im_start|>system name=example-user\n`
            return message.additional_kwargs["prefix"]
        if isinstance(message, HumanMessage):
            return self.human_prefix or ""
        if isinstance(message, AIMessage):
            return self.ai_prefix or ""
        if isinstance(message, SystemMessage):
            return self.system_prefix or ""
        if isinstance(message, ToolMessage):
            return self.tool_prefix or ""
        if isinstance(message, ChatMessage):
            # I can't decide the prefix for ChatMessage
            return message.role
        # BaseMessages fall here
        match message.type:
            case "human":
                return self.human_prefix or ""
            case "ai":
                return self.ai_prefix or ""
            case "system":
                return self.system_prefix or ""
            case "tool":
                return self.tool_prefix or ""
            case "chat":
                return message.role
            case _:
                raise ValueError(f"Got unsupported message type: {message}")

    def get_suffix(self, message: BaseMessage) -> str:
        if "suffix" in message.additional_kwargs:
            # allow custom suffix
            return message.additional_kwargs["suffix"]
        if isinstance(message, HumanMessage):
            return self.human_suffix or ""
        if isinstance(message, AIMessage):
            return self.ai_suffix or ""
        if isinstance(message, SystemMessage):
            return self.system_suffix or ""
        if isinstance(message, ToolMessage):
            return self.tool_suffix or ""
        if isinstance(message, ChatMessage):
            # I can't decide the suffix for ChatMessage
            return ""
        # BaseMessages fall here
        match message.type:
            case "human":
                return self.human_suffix or ""
            case "ai":
                return self.ai_suffix or ""
            case "system":
                return self.system_suffix or ""
            case "tool":
                return self.tool_suffix or ""
            case "chat":
                return ""
            case _:
                raise ValueError(f"Got unsupported message type: {message}")
