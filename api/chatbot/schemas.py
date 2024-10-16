from copy import deepcopy
from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field, field_validator

from chatbot.utils import utcnow


class ChatMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    parent_id: str | None = None
    id: str = Field(default_factory=lambda: str(uuid4()))
    """Message id, used to chain stream responses into message."""
    conversation: str | None = None
    """Conversation id"""
    from_: str | None = Field(None, alias="from")
    """A transient field to determine conversation id."""
    content: str | list[str | dict] | None = None
    type: Literal[
        "text", "stream/start", "stream/text", "stream/end", "info", "error"
    ] = "text"
    feedback: Literal["thumbup", "thumbdown", None] = None
    additional_kwargs: dict[str, Any] | None = None

    @staticmethod
    def from_lc(
        lc_message: BaseMessage, conv_id: str, from_: str = None
    ) -> "ChatMessage":
        additional_kwargs = deepcopy(lc_message.additional_kwargs)
        return ChatMessage(
            parent_id=additional_kwargs.pop("parent_id", None),
            id=lc_message.id or str(uuid4()),
            conversation=conv_id or additional_kwargs.pop("session_id", None),
            from_=from_ or lc_message.type,
            content=lc_message.content,
            type=additional_kwargs.pop("type", "text"),
            feedback=additional_kwargs.pop("feedback", None),
            additional_kwargs=additional_kwargs,
        )

    def to_lc(self) -> BaseMessage:
        """Convert to langchain message.
        Note: for file messages, the content is used for LLM, and other fields are used for displaying to frontend.
        """
        additional_kwargs = (self.additional_kwargs or {}) | {
            "type": self.type,
            "session_id": self.conversation,
        }
        if self.parent_id:
            additional_kwargs["parent_id"] = self.parent_id
        if self.feedback:
            additional_kwargs["feedback"] = self.feedback
        match self.from_:
            case "system":
                return SystemMessage(
                    id=self.id,
                    content=self.content,
                    additional_kwargs=additional_kwargs,
                )
            case "ai":
                return AIMessage(
                    id=self.id,
                    content=self.content,
                    additional_kwargs=additional_kwargs,
                )
            case _:  # username
                return HumanMessage(
                    id=self.id,
                    content=self.content,
                    additional_kwargs=additional_kwargs,
                )

    def model_dump(
        self, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> dict[str, Any]:
        return super().model_dump(
            by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )

    def model_dump_json(
        self, by_alias: bool = True, exclude_none: bool = True, **kwargs
    ) -> str:
        return super().model_dump_json(
            by_alias=by_alias, exclude_none=exclude_none, **kwargs
        )


class AIChatMessage(ChatMessage):
    from_: Literal["ai"] = Field("ai", alias="from")


class AIChatStartMessage(AIChatMessage):
    content: Literal[None] = None
    type: Literal["stream/start"] = "stream/start"


class AIChatEndMessage(AIChatMessage):
    content: Literal[None] = None
    type: Literal["stream/end"] = "stream/end"


class InfoMessage(ChatMessage):
    from_: Literal["system"] = Field("system", alias="from")
    content: dict[str, Any]
    type: Literal["info"] = "info"


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

    messages: list[ChatMessage] = []


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
    source_id: str


class UserProfile(BaseModel):
    userid: str
    username: str | None = None
    email: str | None = None
