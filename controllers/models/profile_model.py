"""Module for Profile tables."""

from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Text, Integer, Boolean
from sqlalchemy import ForeignKey
from typing import Optional


class Profile(BaseModel):
    """Profile model."""

    __tablename__ = "profiles"

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    first_name: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    last_name: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    about: Mapped[Optional[str]] = MappedColumn(
        Text,
        nullable=True
    )

    location: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    email: Mapped[Optional[str]] = MappedColumn(
        String(255),
        unique=True, 
        nullable=True
    )

    contact_email: Mapped[Optional[str]] = MappedColumn(
        String(255),
        nullable=True
    )

    gender: Mapped[Optional[str]] = MappedColumn(
        String(1),
        nullable=True
    )

    age: Mapped[Optional[int]] = MappedColumn(
        Integer,
        nullable=True
    )

    user_type: Mapped[Optional[str]] = MappedColumn(
        String(20),
        nullable=True,
        comment="student, company, professor, admin"
    )

    profile_img: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    banner_img: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    phone_number: Mapped[Optional[str]] = MappedColumn(
        String(20),
        nullable=True
    )

    is_verified: Mapped[bool] = MappedColumn(
        Boolean,
        nullable=False,
        default=False
    )
