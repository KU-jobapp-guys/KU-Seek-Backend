"""Controller for Education CRUD operations."""

from typing import List, Dict, Optional, Union
from sqlalchemy.orm import Session
from connexion.exceptions import ProblemException
from .models.profile_model import Education
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID


class EducationController:
    """Controller to use CRUD operations for Education."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    def get_educations_by_user(
        self,
        user_id: Union[str, UUID],
        session: Optional[Session] = None,
    ) -> List[Dict]:
        """Return all educations belonging to a specific user.

        If a `session` is provided, the method will reuse it and will not
        open/close a new connection. This prevents nested connections when
        higher-level controllers already have an active session (pool_size=1).
        """
        created_session = False
        if session is None:
            session = self.db.get_session()
            created_session = True

        education_obj = []
        try:
            uid = user_id
            try:
                if not isinstance(user_id, UUID):
                    uid = UUID(str(user_id))
            except Exception:
                uid = user_id

            educations = (
                session.query(Education)
                .filter(Education.user_id == uid)
                .all()
            )

            for e in educations:
                education_obj.append({
                    "id": e.id,
                    "curriculumName": e.curriculum_name,
                    "university": e.university,
                    "major": e.major,
                    "yearOfStudy": e.year_of_study.year,
                    "graduateYear": e.graduate_year.year,
                })
            return education_obj
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error fetching educations for user {user_id}: {e}")
        finally:
            if created_session:
                session.close()


    def post_education(self, user_id: UUID, body: Dict) -> Dict:
        """Create a new education record.

        Expects fields: curriculum_name, university, major, year_of_study, graduate_year
        """
        if not body:
            raise ProblemException("Request body cannot be empty.")

        required = [
            "curriculum_name",
            "university",
            "major",
            "year_of_study",
            "graduate_year",
        ]
        missing = [f for f in required if f not in body]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        session = self.db.get_session()
        try:
            edu = Education(user_id=user_id)
            for k, v in body.items():
                if hasattr(edu, k):
                    setattr(edu, k, v)

            session.add(edu)
            session.commit()
            session.refresh(edu)

            return edu.to_dict()

        except Exception as e:
            session.rollback()
            session.close()
            raise ProblemException(str(e))
        finally:
            session.close()

    def patch_education(self, education_id: int, body: Dict) -> Dict:
        """Update an education record with partial fields."""
        if not body:
            raise ProblemException("Request body cannot be empty.")

        session = self.db.get_session()
        try:
            edu = (
                session.query(Education)
                .where(Education.id == education_id)
                .one_or_none()
            )
            if not edu:
                raise ValueError(f"Education with id={education_id} not found")

            for k, v in body.items():
                if hasattr(edu, k):
                    setattr(edu, k, v)

            session.commit()
            return edu.to_dict()

        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(str(e))
        finally:
            session.close()

    def delete_education(self, education_id: int) -> Dict:
        """Delete an education record by id."""
        session = self.db.get_session()
        try:
            edu = (
                session.query(Education)
                .where(Education.id == education_id)
                .one_or_none()
            )
            if not edu:
                raise ValueError(f"Education with id={education_id} not found")

            data = edu.to_dict()
            session.delete(edu)
            session.commit()
            return data

        except SQLAlchemyError as e:
            session.rollback()
            raise RuntimeError(str(e))
        finally:
            session.close()
