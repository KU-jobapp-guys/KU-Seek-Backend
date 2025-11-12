"""Controller for Education CRUD operations."""

from typing import List, Dict, Optional
from connexion.exceptions import ProblemException
from .models.profile_model import Education
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID


class EducationController:
    """Controller to use CRUD operations for Education."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    def get_educations_by_user(self, user_id: UUID) -> List[Dict]:
        """Return all educations belonging to a specific user."""
        session = self.db.get_session()
        education_obj = []
        try:
            educations = (
                session.query(Education)
                .filter(Education.user_id == user_id)
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
