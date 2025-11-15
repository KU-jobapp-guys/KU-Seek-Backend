"""Module for admin request models."""

import uuid
import enum
from datetime import datetime
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import ForeignKey, DateTime, Integer, func
from sqlalchemy.types import Enum
from .user_model import UserTypes


class RequestStatusTypes(enum.Enum):
    """Enumeration of request codes."""

    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"


class UserRequest(BaseModel):
    """User creation request model."""

    __tablename__ = "user_requests"
    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    requested_type: Mapped[Enum] = MappedColumn(Enum(UserTypes))
    status: Mapped[Enum] = MappedColumn(
        Enum(RequestStatusTypes), default=RequestStatusTypes.PENDING
    )
    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )
    verification_document: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("files.id", ondelete="SET NULL"), nullable=False
    )
    approved_at: Mapped[datetime] = MappedColumn(DateTime, nullable=True)
    approved_by: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class JobRequest(BaseModel):
    """Job creation request model."""

    __tablename__ = "job_requests"
    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[Enum] = MappedColumn(
        Enum(RequestStatusTypes), default=RequestStatusTypes.PENDING
    )
    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )
    approved_at: Mapped[datetime] = MappedColumn(DateTime, nullable=True)
    approved_by: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False
    )
