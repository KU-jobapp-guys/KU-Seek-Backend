"""Controller for Education CRUD operations."""

from typing import List, Dict, Optional
from connexion.exceptions import ProblemException
from .models.profile_model import Education
from .models.user_model import Student
from uuid import UUID
from .auth_controller import get_auth_user_id
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

    