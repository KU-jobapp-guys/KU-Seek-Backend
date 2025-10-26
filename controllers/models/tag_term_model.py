"""Module for Tag and Term tables."""

from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Integer


class Tags(BaseModel):
    """Tags model."""

    __tablename__ = "tags"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = MappedColumn(String(40), nullable=True)


class Terms(BaseModel):
    """Terms model."""

    __tablename__ = "terms"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = MappedColumn(String(40), nullable=True)
    type: Mapped[str] = MappedColumn(String(40), nullable=True)

