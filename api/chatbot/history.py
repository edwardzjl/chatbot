from uuid import uuid4

from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import AIMessage, HumanMessage

from chatbot.utils import utcnow


class CustomRedisChatMessageHistory(RedisChatMessageHistory):
    """Persist extra information in `additional_kwargs`."""

    def add_user_message(self, message: str) -> None:
        """Add an AI message to the store"""
        self.add_message(
            HumanMessage(
                content=message.strip(),
                additional_kwargs={
                    "id": uuid4().hex,
                    "sent_at": utcnow().isoformat(),
                    "type": "text",
                },
            )
        )

    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the store"""
        self.add_message(
            AIMessage(
                content=message.strip(),
                additional_kwargs={
                    "id": uuid4().hex,
                    "sent_at": utcnow().isoformat(),
                    "type": "text",
                },
            )
        )
