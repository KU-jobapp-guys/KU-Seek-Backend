"""Module for Profile tables."""

import uuid

from datetime import date, datetime
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, func
from sqlalchemy import ForeignKey
from typing import Optional


class Profile(BaseModel):
    """Profile model."""

    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    first_name: Mapped[Optional[str]] = MappedColumn(String(100), nullable=True)

    last_name: Mapped[Optional[str]] = MappedColumn(String(100), nullable=True)

    about: Mapped[Optional[str]] = MappedColumn(Text, nullable=True)

    location: Mapped[Optional[str]] = MappedColumn(String(100), nullable=True)

    email: Mapped[Optional[str]] = MappedColumn(String(255), unique=True, nullable=True)

    contact_email: Mapped[Optional[str]] = MappedColumn(String(255), nullable=True)

    gender: Mapped[Optional[str]] = MappedColumn(String(1), nullable=True)

    age: Mapped[Optional[int]] = MappedColumn(Integer, nullable=True)

    user_type: Mapped[Optional[str]] = MappedColumn(
        String(20), nullable=True, comment="student, company, professor, admin"
    )

    profile_img: Mapped[Optional[str]] = MappedColumn(String(100), nullable=True)

    banner_img: Mapped[Optional[str]] = MappedColumn(String(100), nullable=True)

    phone_number: Mapped[Optional[str]] = MappedColumn(String(20), nullable=True)

    is_verified: Mapped[bool] = MappedColumn(Boolean, nullable=False, default=False)


class ProfileSkills(BaseModel):
    """Profile skills model."""

    __tablename__ = "profile_skills"

    user_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    skill_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class Education(BaseModel):
    """Education model."""

    __tablename__ = "educations"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    curriculum_name: Mapped[str] = MappedColumn(String(255), nullable=False)

    university: Mapped[str] = MappedColumn(String(255), nullable=False)

    major: Mapped[str] = MappedColumn(String(255), nullable=False)

    year_of_study: Mapped[date] = MappedColumn(Date, nullable=False)

    graduate_year: Mapped[date] = MappedColumn(Date, nullable=False)


class StudentDocuments(BaseModel):
    """Student documents model."""

    __tablename__ = "student_documents"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    student_id: Mapped[int] = MappedColumn(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )

    file_path: Mapped[str] = MappedColumn(String(255), nullable=False)

    original_filename: Mapped[str] = MappedColumn(String(255), nullable=False)

    uploaded_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )


class StudentHistories(BaseModel):
    """Student histories model."""

    __tablename__ = "student_histories"

    job_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    student_id: Mapped[int] = MappedColumn(
        ForeignKey("students.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    viewed_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )


class ProfessorConnections(BaseModel):
    """Professor connections model."""

    __tablename__ = "professor_connections"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    professor_id: Mapped[int] = MappedColumn(
        ForeignKey("professors.id", ondelete="CASCADE"), nullable=False
    )

    company_id: Mapped[int] = MappedColumn(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )


class Announcements(BaseModel):
    """Announcements model."""

    __tablename__ = "announcements"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)

    professor_id: Mapped[int] = MappedColumn(
        ForeignKey("professors.id", ondelete="CASCADE"), nullable=False
    )

    title: Mapped[str] = MappedColumn(String(255), nullable=False)

    content: Mapped[str] = MappedColumn(Text, nullable=False)

    created_at: Mapped[datetime] = MappedColumn(
        DateTime, default=func.now(), nullable=False
    )
