from datetime import datetime
from typing import Optional

from aredis_om import JsonModel, Field
from pydantic import BaseModel, root_validator


class StreamResponse(BaseModel):
    id: str
    "Message id, used to chain stream responses into message."
    text: str


class Conversation(JsonModel):
    id: Optional[str]
    title: str
    owner: str = Field(index=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
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
