from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from aredis_om import JsonModel, Field
from langchain.schema import BaseMessage
from pydantic import BaseModel, root_validator, validator

from chatbot.utils import utcnow


class ChatMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    "Message id, used to chain stream responses into message."
    from_: Optional[str] = Field(alias="from")
    to: Optional[str]
    """A transient field to determine conversation id."""
    content: Optional[str]
    type: str
    # sent_at is not an important information for the user, as far as I can tell.
    # But it introduces some complexity in the code, so I'm removing it for now.
    # sent_at: datetime = Field(default_factory=datetime.now)

    @validator("type")
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

    _encoders_by_type = {
        datetime: lambda dt: dt.isoformat(timespec="seconds"),
        UUID: lambda uid: uid.hex,
    }

    def _iter(self, **kwargs):
        for key, value in super()._iter(**kwargs):
            yield key, self._encoders_by_type.get(type(value), lambda v: v)(value)

    def dict(
        self, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> dict[str, Any]:
        return super().dict(by_alias=by_alias, exclude_none=exclude_none, **kwargs)

    class Config:
        allow_population_by_field_name = True
        """'from' is a reversed word in python, so we have to populate ChatMessage by 'from_'"""


class Conversation(JsonModel):
    id: Optional[str]
    title: str
    owner: str = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = created_at

    # TODO: this is not clear as the model will return both a 'pk' and an 'id' with the same value.
    # But I think id is more general than pk.
    @root_validator(pre=True)
    def set_id(cls, values):
        if "pk" in values:
            values["id"] = values["pk"]
        return values


class ConversationDetail(Conversation):
    """Conversation with messages."""

    messages: list[dict[str, str]] = []


class UpdateConversation(BaseModel):
    title: str
