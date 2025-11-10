from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, DateTime, Boolean,func
from datetime import datetime
import uuid


class TOSAgreement(BaseModel):
    """Model storing user's terms of service agreement and time."""

    __tablename__ = "tos"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    agree_status: Mapped[bool] = MappedColumn(
        Boolean, nullable=False
        )

    agreed_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )
