from __future__ import annotations

from copy import deepcopy

from datetime import datetime
from typing import Any, Literal, NotRequired, Type, TypedDict
from uuid import UUID, uuid4

from langchain_core.messages import BaseMessage, _message_from_dict
from pydantic import BaseModel, ConfigDict, Field, field_validator

from chatbot.utils import utcnow


# LESSON 1: AVOID using Pydantic model for attributes of `additional_kwargs`.
#   It will be a Pydantic model instance upon initialization but a plain dictionary after deserialization.
#   This type inconsistency can lead to significant issues when you try to use it.
# LESSON 2: NamedTuple will raise an exception when encountering unexpected keyword arguments.
class Attachment(TypedDict):
    url: str
    mimetype: NotRequired[str | None] = None
    size: NotRequired[int] = 0


class ChatMessage(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    parent_id: str | None = None
    id: str = Field(default_factory=lambda: str(uuid4()))
    """Message id, used to chain stream responses into message."""
    conversation: str | None = None
    """Conversation id"""
    from_: str | None = Field(None, alias="from")
    """A transient field to determine conversation id."""
    content: str | list[str | dict] | None = None
    attachments: list[Attachment] | None = None
    type: str
    sent_at: datetime | None = Field(default_factory=utcnow)
    additional_kwargs: dict[str, Any] | None = None

    @staticmethod
    def from_lc(lc_message: BaseMessage, **kwargs) -> ChatMessage:
        additional_kwargs = deepcopy(lc_message.additional_kwargs)

        # NOTE: By this we extend the `type` field of langchain message to support more types.
        msg_type = additional_kwargs.pop("type", lc_message.type)

        msg_class = message_class_map.get(msg_type, ChatMessage)

        sent_at = additional_kwargs.pop("sent_at", None)
        _kwargs = {
            "parent_id": additional_kwargs.pop("parent_id", None),
            "id": lc_message.id or str(uuid4()),
            "conversation": additional_kwargs.pop("session_id", None),
            "from": lc_message.name,
            "content": lc_message.content,
            "type": msg_type,
            "sent_at": datetime.fromisoformat(sent_at) if sent_at else None,
            "additional_kwargs": additional_kwargs,
        }

        if feedback := additional_kwargs.pop("feedback", None):
            _kwargs["feedback"] = feedback

        if attachments := additional_kwargs.pop("attachments", None):
            _kwargs["attachments"] = attachments

        _kwargs = _kwargs | kwargs
        return msg_class(**_kwargs)

    def to_lc(self) -> BaseMessage:
        """Convert to langchain message."""
        additional_kwargs = (self.additional_kwargs or {}) | {
            "type": self.type,
            "session_id": self.conversation,
        }
        if self.sent_at:
            additional_kwargs["sent_at"] = self.sent_at.isoformat()
        if self.parent_id:
            additional_kwargs["parent_id"] = self.parent_id
        if hasattr(self, "feedback"):
            additional_kwargs["feedback"] = self.feedback
        if self.attachments:
            additional_kwargs["attachments"] = self.attachments

        kwargs = {
            "id": self.id,
            "name": self.from_,
            "content": self.content,
            "additional_kwargs": additional_kwargs,
        }

        return _message_from_dict({"type": self.type, "data": kwargs})

    def model_dump(
        self, *, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> dict[str, Any]:
        return super().model_dump(
            by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )

    def model_dump_json(
        self, *, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> str:
        return super().model_dump_json(
            by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )


class HumanChatMessage(ChatMessage):
    type: Literal["human"] = "human"


class AIChatMessage(ChatMessage):
    type: Literal["ai"] = "ai"
    feedback: Literal["thumbup", "thumbdown", None] = None


class AIChatMessageChunk(AIChatMessage):
    type: Literal["AIMessageChunk"] = "AIMessageChunk"


class InfoMessage(ChatMessage):
    content: dict[str, Any]
    type: Literal["info"] = "info"


message_class_map: dict[str, Type[ChatMessage]] = {
    "human": HumanChatMessage,
    "ai": AIChatMessage,
    "AIMessageChunk": AIChatMessageChunk,
    "info": InfoMessage,
}


class Conversation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID | None = None
    title: str
    owner: str
    pinned: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    last_message_at: datetime = created_at

    @field_validator("id")
    @classmethod
    def convert_id(cls, v: UUID) -> str:
        return str(v)


class ConversationDetail(Conversation):
    """Conversation with messages."""

    # TODO: This sucks. If we only return ChatMessage, fields in the child classes will be lost.
    messages: list[HumanChatMessage | AIChatMessage] = []


class CreateConversation(BaseModel):
    title: str


class UpdateConversation(BaseModel):
    title: str | None = None
    pinned: bool | None = None


class Share(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | UUID | None = None
    title: str
    url: str
    owner: str
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("id")
    @classmethod
    def convert_id(cls, v: UUID) -> str:
        return str(v)


class CreateShare(BaseModel):
    title: str
    source_id: UUID


class UserProfile(BaseModel):
    userid: str
    username: str | None = None
    email: str | None = None
