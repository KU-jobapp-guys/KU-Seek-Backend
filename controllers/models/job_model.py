"""Module for Job tables."""

import uuid

from datetime import datetime
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean
from sqlalchemy import ForeignKey, func, UniqueConstraint
from typing import Optional


class Job(BaseModel):
    """Job model."""

    __tablename__ = "jobs"
    
    id: Mapped[int] = MappedColumn(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    
    company_id: Mapped[Optional[int]] = MappedColumn(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )
    
    description: Mapped[Optional[str]] = MappedColumn(
        Text, 
        nullable=True
    )
    
    title: Mapped[Optional[str]] = MappedColumn(
        String(50), 
        nullable=False
    )
    
    salary_min: Mapped[Optional[float]] = MappedColumn(
        Float, 
        nullable=False
    )
    
    salary_max: Mapped[Optional[float]] = MappedColumn(
        Float, 
        nullable=False
    )
    
    location: Mapped[Optional[str]] = MappedColumn(
        String(255), 
        nullable=False
    )
    
    work_hours: Mapped[Optional[str]] = MappedColumn(
        String(20), 
        nullable=False
    )
    
    job_type: Mapped[Optional[str]] = MappedColumn(
        String(40), 
        nullable=False
    )
    
    job_level: Mapped[Optional[str]] = MappedColumn(
        String(40), 
        nullable=False
    )
    
    status: Mapped[str] = MappedColumn(
        String(20),
        default="pending",
        nullable=False,
        comment="pending, approved, rejected"
    )
    
    visibility: Mapped[Optional[bool]] = MappedColumn(
        Boolean,
        default=False,
        nullable=False
    )
    
    capacity: Mapped[Optional[int]] = MappedColumn(
        Integer, 
        nullable=False
    )
    
    end_date: Mapped[Optional[datetime]] = MappedColumn(
        DateTime, 
        nullable=False
    )
    
    created_at: Mapped[datetime] = MappedColumn(
        DateTime, 
        default=func.now(), 
        nullable=False
    )
    
    approved_by: Mapped[Optional[uuid.UUID]] = MappedColumn(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False
    )


class JobSkills(BaseModel):
    """job skills model."""

    __tablename__ = "job_skills"

    job_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("jobs.id", ondelete="CASCADE"), 
        primary_key=True,
        nullable=False
    )
    skill_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("terms.id", ondelete="CASCADE"), 
        primary_key=True,
        nullable=False
    )


class JobTags(BaseModel):
    """job tags model."""

    __tablename__ = "job_tags"

    job_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("jobs.id", ondelete="CASCADE"), 
        primary_key=True,
        nullable=False
    )
    tag_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("tags.id", ondelete="CASCADE"), 
        primary_key=True,
        nullable=False
    )


class JobApplication(BaseModel):
    """Job application model."""

    __tablename__ = "job_applications"

    id: Mapped[int] = MappedColumn(
        Integer, 
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("jobs.id", ondelete="CASCADE"), 
        nullable=False
    )

    student_id: Mapped[int] = MappedColumn(
        Integer, 
        ForeignKey("students.id", ondelete="CASCADE"), 
        nullable=False
    )

    resume: Mapped[str] = MappedColumn(
        String(500),
        nullable=False
    )

    letter_of_application: Mapped[str] = MappedColumn(
        String(500),
        nullable=False
    )

    additional_document: Mapped[Optional[str]] = MappedColumn(
        String(500),
        nullable=True
    )

    phone_number: Mapped[str] = MappedColumn(
        String(12),
        nullable=False
    )

    status: Mapped[str] = MappedColumn(
        String(30),
        default="pending",
        nullable=False,
        comment="pending, accepted, rejected"
    )

    applied_at: Mapped[datetime] = MappedColumn(
        DateTime,
        default=func.now(),
        nullable=False
    )


class Bookmark(BaseModel):
    """Model for Bookmark Table."""

    __tablename__ = "bookmarks"

    
    __table_args__ = (
        UniqueConstraint('student_id', 'job_id', name='unique_student_job'),
    )

    id: Mapped[int] = MappedColumn(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    job_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    student_id: Mapped[int] = MappedColumn(
        Integer,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = MappedColumn(
        DateTime,
        default=func.now(),
        nullable=False
    )
