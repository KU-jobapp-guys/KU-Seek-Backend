"""Module for User tables."""

import enum
from .base_model import BaseModel
from sqlalchemy.types import Enum
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String
import uuid


class UserTypes(enum.Enum):
    """Enumeration of user classes."""

    STUDENT = "Student"
    COMPANY = "Company"
    STAFF = "Staff"
    PROFESSOR = "Professor"


class User(BaseModel):
    """Base user model."""

    __tablename__ = "User"
    id: Mapped[uuid.UUID] = MappedColumn(primary_key=True, default=uuid.uuid4)
    google_uid: Mapped[str] = MappedColumn(String(100), nullable=False)
    email: Mapped[str] = MappedColumn(String(100), nullable=False)
    is_verified: Mapped[bool] = MappedColumn(default=False)
    type: Mapped[Enum] = MappedColumn(Enum(UserTypes))
