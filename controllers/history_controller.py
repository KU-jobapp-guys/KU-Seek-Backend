"""Module for Student history endpoints."""

from typing import List, Dict
from uuid import UUID
from datetime import datetime
from connexion.exceptions import ProblemException
from flask import request
from .decorators import role_required
from .models.profile_model import StudentHistories
from .models.user_model import Student
from .auth_controller import get_auth_user_id


class HistoryController:
    """Controller for handling student view histories."""

    def __init__(self, database):
        """Initialize the class with a database instance."""
        self.db = database

    @role_required(["Student"])
    def get_histories(self) -> List[Dict]:
        """Return all history entries for the authenticated student.

        Uses the authenticated user's token to resolve the student record and
        returns a list of StudentHistories rows as dictionaries.
        """
        session = self.db.get_session()
        try:
            uid = get_auth_user_id(request)
            student = (
                session.query(Student)
                .where(Student.user_id == UUID(uid))
                .one_or_none()
            )

            if not student:
                raise ProblemException("Student not found")

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

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
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
            raise ProblemException("'job_id' is a required property")

        session = self.db.get_session()
        try:
            uid = get_auth_user_id(request)
            student = (
                session.query(Student)
                .where(Student.user_id == UUID(uid))
                .one_or_none()
            )

            if not student:
                raise ProblemException("Student not found")

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
                existing.viewed_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                return {
                    "job_id": existing.job_id,
                    "student_id": existing.student_id,
                    "viewed_at": existing.viewed_at.isoformat()
                    if existing.viewed_at
                    else None,
                }

            history = StudentHistories(job_id=job_id, student_id=student.id)
            session.add(history)
            session.commit()
            session.refresh(history)

            return {
                "job_id": history.job_id,
                "student_id": history.student_id,
                "viewed_at": history.viewed_at.isoformat()
                if history.viewed_at
                else None,
            }

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()
