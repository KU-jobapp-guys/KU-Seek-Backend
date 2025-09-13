"""Module for User tables."""

from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String
import uuid


class User(BaseModel):
    """Base user model."""

    __tablename__ = "User"
    id: Mapped[uuid.UUID] = MappedColumn(primary_key=True, default=uuid.uuid4)
    google_uid: Mapped[str] = MappedColumn(String(100), nullable=False)
    email: Mapped[str] = MappedColumn(String(100), nullable=False)
    password: Mapped[str] = MappedColumn(String(100))
    is_admin: Mapped[bool] = MappedColumn(default=False)
