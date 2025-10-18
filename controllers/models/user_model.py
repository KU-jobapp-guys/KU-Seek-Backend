"""Module for User tables."""

import enum
from typing import Optional
from .base_model import BaseModel
from sqlalchemy.types import Enum
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Integer, ForeignKey, DECIMAL, Text
import uuid


class UserTypes(enum.Enum):
    """Enumeration of user classes."""

    STUDENT = "Student"
    COMPANY = "Company"
    STAFF = "Staff"
    PROFESSOR = "Professor"


class User(BaseModel):
    """Base user model."""

    __tablename__ = "users"
    id: Mapped[uuid.UUID] = MappedColumn(primary_key=True, default=uuid.uuid4)
    google_uid: Mapped[str] = MappedColumn(String(100), nullable=False)
    email: Mapped[str] = MappedColumn(String(100), nullable=False)
    is_verified: Mapped[bool] = MappedColumn(default=False)
    type: Mapped[Enum] = MappedColumn(Enum(UserTypes))


class Student(BaseModel):
    """Student model."""

    __tablename__ = "students"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    nisit_id: Mapped[str] = MappedColumn(String(255), unique=True, nullable=False)

    education_id: Mapped[Optional[int]] = MappedColumn(
        Integer, ForeignKey("educations.id", ondelete="SET NULL"), nullable=True
    )

    gpa: Mapped[float] = MappedColumn(DECIMAL(3, 2), nullable=False)

    interests: Mapped[str] = MappedColumn(Text, nullable=False)


class Professor(BaseModel):
    """Professor model."""

    __tablename__ = "professors"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    department: Mapped[str] = MappedColumn(String(255), nullable=False)

    position: Mapped[str] = MappedColumn(String(255), nullable=False)

    office_location: Mapped[str] = MappedColumn(String(255), nullable=False)

    education_id: Mapped[Optional[int]] = MappedColumn(
        Integer, ForeignKey("educations.id", ondelete="SET NULL"), nullable=True
    )

    research_interests: Mapped[str] = MappedColumn(Text, nullable=False)

    description: Mapped[str] = MappedColumn(Text, nullable=False)


class Company(BaseModel):
    """Company model."""

    __tablename__ = "companies"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    company_name: Mapped[str] = MappedColumn(String(255), nullable=False)

    company_type: Mapped[str] = MappedColumn(String(255), nullable=False)

    company_industry: Mapped[str] = MappedColumn(String(255), nullable=False)

    company_overview: Mapped[str] = MappedColumn(Text, nullable=True)

    company_size: Mapped[str] = MappedColumn(String(255), nullable=False)

    company_website: Mapped[str] = MappedColumn(String(255), nullable=False)

    full_location: Mapped[str] = MappedColumn(String(255), nullable=False)
