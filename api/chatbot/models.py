from datetime import datetime

from aredis_om import JsonModel, Field

from chatbot.utils import utcnow


class Conversation(JsonModel):
    title: str
    owner: str = Field(index=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = created_at
