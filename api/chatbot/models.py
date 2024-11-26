from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from chatbot.utils import utcnow


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(Text, index=True)
    pinned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )


class Share(Base):
    __tablename__ = "share"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(Text, index=True)
    url: Mapped[str] = mapped_column(Text)
    snapshot_ref: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )
