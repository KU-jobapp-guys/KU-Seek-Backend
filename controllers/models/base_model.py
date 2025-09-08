"""Module containing the base class that all ORM classes inherit from."""
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Basic model without configurations."""

    pass
