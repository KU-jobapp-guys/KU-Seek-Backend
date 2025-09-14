"""Module containing the base class that all ORM classes inherit from."""

from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Basic model without custom meta constructor configurations."""

    def to_dict(self) -> dict[any]:
        """Return the model as a dictonary."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
