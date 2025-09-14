"""Module for User tables."""

from datetime import date
from typing import Optional
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Integer, Date, ForeignKey, DECIMAL, Text
import uuid


class User(BaseModel):
    """Base user model."""

    __tablename__ = "User"
    id: Mapped[uuid.UUID] = MappedColumn(primary_key=True, default=uuid.uuid4)
    google_uid: Mapped[str] = MappedColumn(String(100), nullable=False)
    email: Mapped[str] = MappedColumn(String(100), nullable=False)
    password: Mapped[str] = MappedColumn(String(100))
    is_admin: Mapped[bool] = MappedColumn(default=False)


class Education(BaseModel):
    """Education model."""

    __tablename__ = "education"

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    curriculum_name: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )

    university: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )

    major: Mapped[str] = MappedColumn(
        String(100),
        nullable=False
    )

    year_of_study: Mapped[date] = MappedColumn(
        Date,
        nullable=False
    )

    graduate_year: Mapped[date] = MappedColumn(
        Date,
        nullable=False
    )


class Student(BaseModel):
    """Student model."""

    __tablename__ = "student"

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    nisit_id: Mapped[str] = MappedColumn(
        String(10),
        unique=True,
        nullable=False
    )

    education: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("education.id", ondelete="SET NULL"),
        nullable=True
    )

    gpa: Mapped[float] = MappedColumn(
        DECIMAL(3, 2),
        nullable=False
    )

    interests: Mapped[str] = MappedColumn(
        Text,
        nullable=False
    )


class Professor(BaseModel):
    """Professor model."""

    __tablename__ = "professor"

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    department: Mapped[str] = MappedColumn(
        String(100),
        nullable=False
    )

    position: Mapped[str] = MappedColumn(
        String(100),
        nullable=False
    )

    office_location: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )


    education: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("education.id", ondelete="SET NULL"),
        nullable=True
    )

    research_interests: Mapped[str] = MappedColumn(
        Text,
        nullable=False
    )

    description: Mapped[str] = MappedColumn(
        Text,
        nullable=False
    )


class Company(BaseModel):
    """Company model."""

    __tablename__ = "company"

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    company_name: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )

    company_type: Mapped[str] = MappedColumn(
        String(50),
        nullable=False
    )

    company_industry: Mapped[str] = MappedColumn(
        String(100),
        nullable=False
    )

    company_size: Mapped[str] = MappedColumn(
        String(50),
        nullable=False
    )

    company_website: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )

    full_location: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )
