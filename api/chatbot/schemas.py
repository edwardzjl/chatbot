from datetime import datetime, timezone
from typing import Optional

from aredis_om import JsonModel, Field
from pydantic import BaseModel, root_validator


class StreamResponse(BaseModel):
    id: str
    "Message id, used to chain stream responses into message."
    text: str


def utcnow():
    """
    datetime.datetime.utcnow() does not contain timezone information.
    """
    return datetime.now(timezone.utc)


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
