"""Module for Profile tables."""

from datetime import date, datetime
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, func
from sqlalchemy import ForeignKey
from typing import Optional


class Profile(BaseModel):
    """Profile model."""

    __tablename__ = "profiles"

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    first_name: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    last_name: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    about: Mapped[Optional[str]] = MappedColumn(
        Text,
        nullable=True
    )

    location: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    email: Mapped[Optional[str]] = MappedColumn(
        String(255),
        unique=True, 
        nullable=True
    )

    contact_email: Mapped[Optional[str]] = MappedColumn(
        String(255),
        nullable=True
    )

    gender: Mapped[Optional[str]] = MappedColumn(
        String(1),
        nullable=True
    )

    age: Mapped[Optional[int]] = MappedColumn(
        Integer,
        nullable=True
    )

    user_type: Mapped[Optional[str]] = MappedColumn(
        String(20),
        nullable=True,
        comment="student, company, professor, admin"
    )

    profile_img: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    banner_img: Mapped[Optional[str]] = MappedColumn(
        String(100),
        nullable=True
    )

    phone_number: Mapped[Optional[str]] = MappedColumn(
        String(20),
        nullable=True
    )

    is_verified: Mapped[bool] = MappedColumn(
        Boolean,
        nullable=False,
        default=False
    )


class ProfileSkills(BaseModel):
    """Profile skills model."""

    __tablename__ = "profile_skills"

    user_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    skill_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("terms.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )


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


class StudentDocument(BaseModel):
    """Student document model."""

    __tablename__ = "student_document"

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    student_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    file_path: Mapped[str] = MappedColumn(
        String(500),
        nullable=False
    )

    original_filename: Mapped[str] = MappedColumn(
        String(255),
        nullable=False
    )

    uploaded_at: Mapped[datetime] = MappedColumn(
        DateTime,
        default=func.now(),
        nullable=False
    )


class StudentHistory(BaseModel):
    """Student history model."""

    __tablename__ = "student_history"

    job_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    student_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    viewed_at: Mapped[datetime] = MappedColumn(
        DateTime,
        default=func.now(),
        nullable=False
    )