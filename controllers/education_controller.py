"""Controller for Education CRUD operations."""

from typing import List, Dict, Optional
from connexion.exceptions import ProblemException
from .models.profile_model import Education
from sqlalchemy.exc import SQLAlchemyError


class EducationController:
    """Controller to use CRUD operations for Education."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    def get_educations(self, education_id: Optional[int] = None) -> List[Dict]:
        """Return all educations or a single education by id.

        If `education_id` is provided, returns a single education dict.
        """
        session = self.db.get_session()
        try:
            if education_id:
                edu = (
                    session.query(Education)
                    .where(Education.id == education_id)
                    .one_or_none()
                )
                if not edu:
                    raise ValueError(f"Education with id={education_id} not found")
                return edu.to_dict()

            educations = session.query(Education).all()
            return [e.to_dict() for e in educations]

        except SQLAlchemyError as e:
            session.close()
            raise RuntimeError(str(e))
        finally:
            session.close()

    def post_education(self, body: Dict) -> Dict:
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
            "user_id"
        ]
        missing = [f for f in required if f not in body]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        session = self.db.get_session()
        try:
            edu = Education()
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
