"""Module for store api that relate to professor."""

from typing import Optional, Dict
from connexion.exceptions import ProblemException
from .models.profile_model import ProfessorConnections, Announcements
from .models.user_model import Professor
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError


class ProfessorController:
    """Controller to use CRUD operations for operation that relate to Professor."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    def get_connection(self, user_id: str):
        """
        Return all connections this Professor have.

        Corresponds to: GET /api/v1/connections

        Args:
            user_id: The unique ID of the user (string format).
        """
        user_uuid = UUID(user_id)


        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor).where(
                    Professor.user_id == user_uuid
                ).one()
            )
            professor_connection = (
                session.query(ProfessorConnections).where(
                    Professor.professor_id == professor.id
                ).all()
            )

            return professor_connection.to_dict

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(status=500, title="Database Error", detail=str(e))
        finally:
            session.close()

    
    def post_connection(self, user_id: str, body: dict):
        """
        Create a new connection for professor.

        Retrieves a single user profile by user id from the MySQL database.

        Args:
            user_id: The unique ID of the user (string format).

        Returns:
            The user profile dictionary if found, otherwise None.
        """
        user_uuid = UUID(user_id)

        if not body:
            raise ProblemException(
                status=400,
                title="Invalid Request",
                detail="Request body cannot be empty.",
            )

        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor).where(
                    Professor.user_id == user_uuid
                ).one_or_none()
            )

            connection = ProfessorConnections(
                professor_id=professor.id,
                company_id=body["company_id"]
            )
           
            session.add(connection)
            session.commit()
        
            connection_data = {
                "id": connection.id,
                "professor_id": connection.professor_id,
                "company_id": connection.company_id,
                "created_at": connection.created_at
            }


        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(status=500, title="Database Error", detail=str(e))
        finally:
            session.close()

        return connection_data
    
    def delete_connection(self, user_id: str):
        pass