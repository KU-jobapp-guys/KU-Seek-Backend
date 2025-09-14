"""Module for User tables."""

from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String


class Task(BaseModel):
    """Testing task model."""

    __tablename__ = "tasks"
    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    name: Mapped[str] = MappedColumn(String(100))
    completed: Mapped[bool] = MappedColumn(default=False)
