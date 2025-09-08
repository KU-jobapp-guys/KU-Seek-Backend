"""Module for User tables."""
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String


class Task(BaseModel):
    """Testing task model."""

    __tablename__ = "tasks"
    id: Mapped[int] = MappedColumn(primary_key=True)
    name: Mapped[str] = MappedColumn(String(100))
    completed: Mapped[bool] = MappedColumn(default=False)

    def to_dict(self):
        """Return the model as a dictonary."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
