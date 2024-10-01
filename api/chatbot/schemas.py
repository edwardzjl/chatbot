from copy import deepcopy
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    content: str | None = None
    type: Literal[
        "text", "stream/start", "stream/text", "stream/end", "info", "error"
    ] = "text"
    feedback: Literal["thumbup", "thumbdown", None] = None
    additional_kwargs: dict[str, Any] | None = None
    # sent_at is not an important information for the user, as far as I can tell.
    # But it introduces some complexity in the code, so I'm removing it for now.
    # sent_at: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def from_lc(
        lc_message: BaseMessage, conv_id: str, from_: str = None
    ) -> "ChatMessage":
        additional_kwargs = deepcopy(lc_message.additional_kwargs)
        return ChatMessage(
            parent_id=additional_kwargs.pop("parent_id", None),
            id=lc_message.id if lc_message.id else str(uuid4()),
            conversation=conv_id,
            from_=from_ or lc_message.type,
            content=lc_message.content,
            type="text",
            feedback=additional_kwargs.pop("feedback", None),
            additional_kwargs=additional_kwargs,
        )

    def to_lc(self) -> BaseMessage:
        """Convert to langchain message.
        Note: for file messages, the content is used for LLM, and other fields are used for displaying to frontend.
        """
        additional_kwargs = (self.additional_kwargs or {}) | {
            "type": self.type,
        }
        if self.parent_id:
            additional_kwargs["parent_id"] = self.parent_id
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
    id: str | None = None
    title: str
    owner: str
    pinned: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    last_message_at: datetime = created_at

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "pk" in values and "id" not in values:
            values["id"] = values["pk"]
        return values


class ConversationDetail(Conversation):
    """Conversation with messages."""

    messages: list[ChatMessage] = []


class CreateConversation(BaseModel):
    title: str


class UpdateConversation(BaseModel):
    title: str | None = None
    pinned: bool | None = None


class Share(BaseModel):
    id: str | None = None
    title: str
    url: str
    owner: str
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="before")
    @classmethod
    def set_id(cls, values):
        if "pk" in values and "id" not in values:
            values["id"] = values["pk"]
        return values


class CreateShare(BaseModel):
    title: str
    source_id: str


class UserProfile(BaseModel):
    userid: str
    username: str | None = None
    email: str | None = None
