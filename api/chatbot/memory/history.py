import json
from typing import Sequence
from uuid import uuid4

from langchain_core.messages import BaseMessage, messages_from_dict

from chatbot.context import session_id
from chatbot.memory.redis import RedisMessageHistory
from chatbot.utils import utcnow


class ChatbotMessageHistory(RedisMessageHistory):
    """Context aware history which also persists extra information in `additional_kwargs`."""

    @property
    def key(self) -> str:
        """Construct the record key to use"""
        return self.key_prefix + (session_id.get() or self.session_id)

    def add_message(self, message: BaseMessage) -> None:
        message.additional_kwargs = (
            default_additional_info() | message.additional_kwargs
        )
        super().add_message(message)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        for message in messages:
            message.additional_kwargs = (
                default_additional_info() | message.additional_kwargs
            )
        super().add_messages(messages)

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        for message in messages:
            message.additional_kwargs = (
                default_additional_info() | message.additional_kwargs
            )
        await super().aadd_messages(messages)

    def windowed_messages(self, window_size: int = 5) -> list[BaseMessage]:
        """Retrieve the last k pairs of messages from Redis"""
        _items = self.client.lrange(self.key, -window_size * 2, -1)
        items = [json.loads(m.decode("utf-8")) for m in _items]
        messages = messages_from_dict(items)
        return messages

    async def awindowed_messages(self, window_size: int = 5) -> list[BaseMessage]:
        """Retrieve the last k pairs of messages from Redis"""
        _items = await self.async_client.lrange(self.key, -window_size * 2, -1)
        items = [json.loads(m.decode("utf-8")) for m in _items]
        messages = messages_from_dict(items)
        return messages


def default_additional_info() -> dict[str, str]:
    return {
        "id": uuid4().hex,
        "sent_at": utcnow().isoformat(),
        "type": "text",
    }
