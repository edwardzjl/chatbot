from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from langchain.schema import BaseMessage
from pydantic import field_validator, model_validator, ConfigDict, BaseModel, Field

from chatbot.utils import utcnow


class ChatMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    """Message id, used to chain stream responses into message."""
    conversation: Optional[str] = None
    """Conversation id"""
    from_: Optional[str] = Field(None, alias="from")
    """A transient field to determine conversation id."""
    content: Optional[str] = None
    type: str
    # sent_at is not an important information for the user, as far as I can tell.
    # But it introduces some complexity in the code, so I'm removing it for now.
    # sent_at: datetime = Field(default_factory=datetime.now)

    @field_validator("type")
    @classmethod
    def validate_message_type(cls, v):
        valid_types = {"start", "stream", "text", "end", "error", "info"}
        if v not in valid_types:
            raise ValueError(f"invalid type {v}, must be one of {valid_types}")
        return v

    @staticmethod
    def from_lc(lc_message: BaseMessage) -> "ChatMessage":
        return ChatMessage(
            from_=lc_message.type,
            content=lc_message.content,
        )

    def model_dump(
        self, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> dict[str, Any]:
        return super().model_dump(
            by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )

    model_config = ConfigDict(populate_by_name=True)


class Conversation(BaseModel):
    id: Optional[str] = None
    title: str
    owner: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = created_at

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "pk" in values and "id" not in values:
            values["id"] = values["pk"]
        return values


class ConversationDetail(Conversation):
    """Conversation with messages."""

    messages: list[dict[str, Any]] = []


class UpdateConversation(BaseModel):
    title: str
