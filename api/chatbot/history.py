from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import BaseMessage, HumanMessage, AIMessage


class AppendSuffixHistory(RedisChatMessageHistory):
    """Append suffix (default to '</s>') to messages as it matches some models' official prompt template."""

    def __init__(self, user_suffix: str = None, ai_suffix: str = "</s>", **kwargs):
        self.user_suffix = user_suffix
        self.ai_suffix = ai_suffix
        super().__init__(**kwargs)

    def add_user_message(self, message: str) -> None:
        """Add an AI message to the store"""
        if self.user_suffix and not message.endswith(self.user_suffix):
            message += self.user_suffix
        super().add_user_message(message)

    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the store"""
        if self.ai_suffix and not message.endswith(self.ai_suffix):
            message += self.ai_suffix
        super().add_ai_message(message)

    @property
    def messages(self) -> list[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""
        messages = [self.remove_message_suffix(message) for message in super().messages]
        return messages

    def remove_message_suffix(self, message: BaseMessage) -> BaseMessage:
        if self.user_suffix and isinstance(message, HumanMessage):
            message.content = message.content[: -len(self.user_suffix)]
        elif self.ai_suffix and isinstance(message, AIMessage):
            message.content = message.content[: -len(self.ai_suffix)]
        return message
