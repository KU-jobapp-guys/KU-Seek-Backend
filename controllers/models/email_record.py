"""Module for email log records."""
import enum
from .base_model import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.types import Enum
from sqlalchemy import String, Integer, func, Text, DateTime
from sqlalchemy.orm import Mapped, MappedColumn


class MailStatus(enum.Enum):
    """Enumeration of mail delivery statuses."""

    MAILSENT = "Sent"
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
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[str]] = MappedColumn(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    status: Mapped[Enum] = MappedColumn(Enum(MailStatus))

    retry_count: Mapped[int] = MappedColumn(Integer, nullable=False, default="0")
