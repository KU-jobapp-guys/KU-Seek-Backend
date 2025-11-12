"""Module for User tables."""

from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.mysql import INTEGER
import uuid


class Token(BaseModel):
    """Model representing refresh tokens issued."""

    __tablename__ = "Tokens"
    uid: Mapped[uuid.UUID] = MappedColumn(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_id: Mapped[int] = MappedColumn(INTEGER(unsigned=True), primary_key=True)
