"""Module for file table."""

import uuid
from datetime import datetime
from .base_model import BaseModel
from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.orm import Mapped, MappedColumn


class File(BaseModel):
    """File model."""

    __tablename__ = "files"
    id: Mapped[uuid.UUID] = MappedColumn(primary_key=True, default=uuid.uuid4)
    owner: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    file_name: Mapped[str] = MappedColumn(String(100), nullable=False)
    file_path: Mapped[str] = MappedColumn(String(100), nullable=False)
    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )
