from datetime import datetime

from aredis_om import Field, JsonModel

from chatbot.utils import utcnow


class Conversation(JsonModel):
    title: str
    owner: str = Field(index=True)
    pinned: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    last_message_at: datetime = created_at

    class Meta:
        global_key_prefix = "chatbot"


class Share(JsonModel):
    title: str
    """Share title, could be different from the source conversation title."""
    owner: str = Field(index=True)
    url: str
    source_id: str = Field(index=True)
    """The original conversation id."""
    created_at: datetime = Field(default_factory=utcnow)

    class Meta:
        global_key_prefix = "chatbot"
