"""Module for email log records."""

import enum
from .base_model import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.types import Enum
from sqlalchemy import String, Integer, func, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, MappedColumn, relationship


class MailStatus(enum.Enum):
    """Enumeration of mail delivery statuses."""

    MAILSENT = "Sent"
    MAILWAIT = "Pending"
    MAILSOFTERROR = "Temporary_Error"
    MAILHARDERROR = "Permanent_Error"


class MailRecord(BaseModel):
    """Mail record model."""

    __tablename__ = "mail_records"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    recipient: Mapped[str] = MappedColumn(String(255), nullable=False)

    topic: Mapped[str] = MappedColumn(String(100), nullable=False)

    body: Mapped[str] = MappedColumn(Text, nullable=False)

    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.utc_timestamp(), nullable=False
    )

    updated_at: Mapped[Optional[str]] = MappedColumn(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    status: Mapped[Enum] = MappedColumn(Enum(MailStatus))

    retry_count: Mapped[int] = MappedColumn(Integer, nullable=False, default="0")


class MailQueue(BaseModel):
    """Unsent mail data model."""

    __tablename__ = "mail_queue"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    recipient: Mapped[str] = MappedColumn(String(255), nullable=False)

    topic: Mapped[str] = MappedColumn(String(100), nullable=False)

    template: Mapped[str] = MappedColumn(String(100), nullable=False)

    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )

    parameters: Mapped[list["MailParameter"]] = relationship(
        "MailParameter",
        back_populates="email",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def get_param(self, key: str):
        """Return the value of a parameter, or None if missing."""
        param = next((p for p in self.parameters if p.key == key), None)
        return param.value if param else None

    def set_param(self, key: str, value: str):
        """Update a parameter."""
        existing = next((p for p in self.parameters if p.key == key), None)
        if existing:
            existing.value = value


class MailParameter(BaseModel):
    """Mail template parameter model."""

    __tablename__ = "mail_parameters"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    email_id: Mapped[int] = MappedColumn(
        ForeignKey("mail_queue.id", ondelete="CASCADE")
    )

    key: Mapped[str] = MappedColumn(String(100), nullable=False)

    value: Mapped[str] = MappedColumn(String(255), nullable=False)

    email: Mapped["MailQueue"] = relationship("MailQueue", back_populates="parameters")
