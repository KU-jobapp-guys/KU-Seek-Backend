"""Module for Job tables."""

from datetime import datetime
from .base_model import BaseModel
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, ForeignKey, func
from typing import Optional


class Job(BaseModel):
    """Job model."""

    __tablename__ = "jobs"
    
    id: Mapped[int] = MappedColumn(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = MappedColumn(Integer,
                                                      ForeignKey("companies.id",
                                                                  ondelete="CASCADE"),
                                                                    nullable=True)
    description: Mapped[Optional[str]] = MappedColumn(Text, nullable=True)
    title: Mapped[Optional[str]] = MappedColumn(String(50), nullable=True)
    salary_min: Mapped[Optional[float]] = MappedColumn(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = MappedColumn(Float, nullable=True)
    location: Mapped[Optional[str]] = MappedColumn(String(255), nullable=True)
    work_hours: Mapped[Optional[str]] = MappedColumn(String(20), nullable=True)
    job_type: Mapped[Optional[str]] = MappedColumn(String(40), nullable=True)
    job_level: Mapped[Optional[str]] = MappedColumn(String(40), nullable=True)
    status: Mapped[str] = MappedColumn(String(20),
                                        default="pending",
                                          nullable=False,
                                            comment="pending, approved, rejected")
    visibility: Mapped[Optional[bool]] = MappedColumn(Boolean, nullable=True)
    capacity: Mapped[Optional[int]] = MappedColumn(Integer, nullable=True)
    end_date: Mapped[Optional[datetime]] = MappedColumn(DateTime, nullable=True)
    created_at: Mapped[datetime] = MappedColumn(DateTime, default=func.now(), nullable=False)
    approved_by: Mapped[Optional[int]] = MappedColumn(Integer,
                                                       ForeignKey("users.id",
                                                                   ondelete="SET NULL"),
                                                                     nullable=True)


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
