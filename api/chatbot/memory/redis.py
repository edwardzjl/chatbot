import json
from typing import Optional, Sequence

import redis
import redis.asyncio as aioredis
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
    messages_to_dict,
)


class RedisMessageHistory(BaseChatMessageHistory):
    """This is basically a rewrite of `langchain_community.chat_message_histories.redis.RedisChatMessageHistory`.
    The main difference is async redis support.
    """

    def __init__(
        self,
        session_id: str,
        url: str = "redis://localhost:6379/0",
        key_prefix: str = "message_store:",
        ttl: Optional[int] = None,
    ):
        # TODO: I might need to dig deeper into redis pooling.
        # Another thing is whether I want to keep both sync and async clients.
        self.client = redis.from_url(url)
        self.async_client = aioredis.from_url(url)
        self.session_id = session_id
        self.key_prefix = key_prefix
        self.ttl = ttl

    @property
    def key(self) -> str:
        """Construct the record key to use"""
        return self.key_prefix + self.session_id

    @property
    def messages(self) -> list[BaseMessage]:  # type: ignore
        """Retrieve the messages from Redis"""
        _items = self.client.lrange(self.key, 0, -1)
        items = [json.loads(m.decode("utf-8")) for m in _items]
        messages = messages_from_dict(items)
        return messages

    async def aget_messages(self) -> list[BaseMessage]:
        _items = await self.async_client.lrange(self.key, 0, -1)
        items = [json.loads(m.decode("utf-8")) for m in _items]
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Redis"""
        self.client.rpush(self.key, json.dumps(message_to_dict(message)))
        if self.ttl:
            self.client.expire(self.key, self.ttl)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        message_dicts = messages_to_dict(messages)
        payload = [json.dumps(m) for m in message_dicts]
        self.client.rpush(self.key, *payload)
        if self.ttl:
            self.client.expire(self.key, self.ttl)

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        message_dicts = messages_to_dict(messages)
        payload = [json.dumps(m) for m in message_dicts]
        await self.async_client.rpush(self.key, *payload)
        if self.ttl:
            self.client.expire(self.key, self.ttl)

    def clear(self) -> None:
        """Clear session memory from Redis"""
        self.client.delete(self.key)

    async def aclear(self) -> None:
        await self.async_client.delete(self.key)
