from uuid import uuid4

from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain.schema import AIMessage, BaseMessage, HumanMessage

from chatbot.utils import utcnow


class CustomRedisChatMessageHistory(RedisChatMessageHistory):
    """Persist extra information in `additional_kwargs`."""

    def add_user_message(self, message: str) -> None:
        """Add an AI message to the store"""
        super().add_message(
            HumanMessage(
                content=message,
                additional_kwargs={
                    "id": uuid4().hex,
                    "sent_at": utcnow().isoformat(),
                    "type": "text",
                },
            )
        )

    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the store"""
        super().add_message(
            AIMessage(
                content=message,
                additional_kwargs={
                    "id": uuid4().hex,
                    "sent_at": utcnow().isoformat(),
                    "type": "text",
                },
            )
        )

    def add_message(self, message: BaseMessage) -> None:
        """Append the message to the record in Redis"""
        additional_info = {
            "id": uuid4().hex,
            "sent_at": utcnow().isoformat(),
            "type": "text",
        }
        message.additional_kwargs = additional_info | message.additional_kwargs
        super().add_message(message)
