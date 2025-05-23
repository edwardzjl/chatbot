from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, Index, Text, TypeDecorator, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from chatbot.utils import utcnow


# See <https://docs.sqlalchemy.org/en/20/core/custom_types.html#store-timezone-aware-timestamps-as-timezone-naive-utc>
# And [this issue](https://github.com/sqlalchemy/sqlalchemy/issues/1985)
class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, insert_default=uuid4)
    title: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(Text, index=True)  # keep this index
    pinned: Mapped[bool] = mapped_column(Boolean, insert_default=False)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime,
        nullable=False,
        insert_default=utcnow,
    )
    last_message_at: Mapped[datetime] = mapped_column(
        TZDateTime,
        nullable=False,
        insert_default=utcnow,
    )
    # And this composite index is for pagination performance.
    __table_args__ = (
        Index(
            "ix_conversation_owner_pinned_last_message_at_id",
            "owner",
            "pinned",
            "last_message_at",
            "id",
        ),
    )


class Share(Base):
    __tablename__ = "share"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, insert_default=uuid4)
    title: Mapped[str] = mapped_column(Text)
    owner: Mapped[str] = mapped_column(Text, index=True)  # keep this index
    url: Mapped[str] = mapped_column(Text)
    snapshot_ref: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime,
        nullable=False,
        insert_default=utcnow,
    )
    __table_args__ = (
        Index("ix_share_owner_created_at_id", "owner", "created_at", "id"),
    )
