"""Module for Student history endpoints."""

from typing import List, Dict
from uuid import UUID
from datetime import datetime, timezone
from swagger_server.openapi_server import models
from flask import request
from .decorators import role_required
from .models.profile_model import StudentHistories
from .models.user_model import Student
from .auth_controller import get_auth_user_id
from logger.custom_logger import get_logger


logger = get_logger()


class HistoryController:
    """Controller for handling student view histories."""

    def __init__(self, database):
        """Initialize the class with a database instance."""
        self.db = database

    @role_required(["Student"])
    def get_histories(self, user_id: str) -> List[Dict]:
        """Return all history entries for the authenticated student.

        Uses the authenticated user's token to resolve the student record and
        returns a list of StudentHistories rows as dictionaries.
        """
        session = self.db.get_session()
        try:
            student = (
                session.query(Student)
                .where(Student.user_id == UUID(user_id))
                .one_or_none()
            )

            if not student:
                session.close()
                return models.ErrorMessage("Student not found"), 404

            histories = (
                session.query(StudentHistories)
                .where(StudentHistories.student_id == student.id)
                .all()
            )

            if not histories:
                return []

            results = [
                {
                    "job_id": h.job_id,
                    "student_id": h.student_id,
                    "viewed_at": h.viewed_at.isoformat() if h.viewed_at else None,
                }
                for h in histories
            ]

            return results

        except Exception as e:
            session.rollback()
            logger.exception("Database error in get_histories: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            session.close()

    @role_required(["Student"])
    def post_history(self, body: Dict) -> Dict:
        """Create or update a history entry for the authenticated student.

        Body must include `job_id` (int).
        If an entry already exists for the (student, job) pair, its viewed_at
        timestamp is updated to now; otherwise a new row is inserted.
        """
        if not body or "job_id" not in body:
            return models.ErrorMessage("'job_id' is a required property"), 400

        def _ensure_trim(session, student_id: int):
            """Ensure the history table for a student is trimmed to 15 rows.

            Keep the newest 15 entries and delete the rest.
            """
            total = (
                session.query(StudentHistories)
                .where(StudentHistories.student_id == student_id)
                .count()
            )
            if total <= 15:
                return

            oldest = (
                session.query(StudentHistories)
                .where(StudentHistories.student_id == student_id)
                .order_by(
                    StudentHistories.viewed_at.asc(),
                    StudentHistories.job_id.asc(),
                    StudentHistories.student_id.asc(),
                )
                .all()
            )

            to_remove = total - 15
            for row in oldest[:to_remove]:
                session.delete(row)

            session.commit()

        session = self.db.get_session()
        try:
            uid = None
            if isinstance(body, dict) and "user_id" in body:
                uid = body.get("user_id")
            uid = uid or get_auth_user_id(request)
            student = (
                session.query(Student).where(Student.user_id == UUID(uid)).one_or_none()
            )

            if not student:
                session.close()
                return models.ErrorMessage("Student not found"), 404

            job_id = body["job_id"]

            existing = (
                session.query(StudentHistories)
                .where(
                    StudentHistories.job_id == job_id,
                    StudentHistories.student_id == student.id,
                )
                .one_or_none()
            )

            if existing:
                existing.viewed_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(existing)
                _ensure_trim(session, student.id)

                return {
                    "job_id": existing.job_id,
                    "student_id": existing.student_id,
                    "viewed_at": existing.viewed_at.isoformat()
                    if existing.viewed_at
                    else None,
                }

            history = StudentHistories(
                job_id=job_id,
                student_id=student.id,
                viewed_at=datetime.now(timezone.utc),
            )
            session.add(history)
            session.commit()
            session.refresh(history)

            _ensure_trim(session, student.id)

            return {
                "job_id": history.job_id,
                "student_id": history.student_id,
                "viewed_at": history.viewed_at.isoformat()
                if history.viewed_at
                else None,
            }

        except Exception as e:
            session.rollback()
            logger.exception("Database error in post_history: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            session.close()
