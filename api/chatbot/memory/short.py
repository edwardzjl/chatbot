import json
from uuid import uuid4

from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict

from chatbot.context import session_id
from chatbot.utils import utcnow


class ShortTermHistory(RedisChatMessageHistory):
    """Short term history that only stores the last `capacity` messages.
    This history is context aware, and also persists extra information in `additional_kwargs`.
    """

    def __init__(self, capacity: int, **kwargs):
        """Create a new short term history.

        Args:
            capacity (int): capacity of the history.

        Raises:
            ValueError: if capacity is not a positive integer.
        """
        if capacity is None or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        super().__init__(**kwargs)
        self.capacity = capacity

    @property
    def key(self) -> str:
        """Construct the record key to use"""
        return self.key_prefix + (session_id.get() or self.session_id)

    @property
    def messages(self) -> list[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""
        _items = self.redis_client.lrange(self.key, 0, self.capacity - 1)
        items = [json.loads(m.decode("utf-8")) for m in _items]
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> list[BaseMessage]:
        """Append the message to the record in Redis.
        Returns messages out of the capacity.
        """
        additional_info = {
            "id": uuid4().hex,
            "sent_at": utcnow().isoformat(),
            "type": "text",
        }
        message.additional_kwargs = additional_info | message.additional_kwargs
        super().add_message(message)
        return self.prune()

    def prune(self) -> list[BaseMessage]:
        """Prune the history to the capacity.
        Returns the pruned messages. Usually only one message is pruned.
        """
        if self.capacity is None:
            return []
        if (to_prune := self.redis_client.llen(self.key) - self.capacity) > 0:
            pruned = self.redis_client.rpop(self.key, to_prune)
            items = [json.loads(m.decode("utf-8")) for m in pruned]
            return messages_from_dict(items)
