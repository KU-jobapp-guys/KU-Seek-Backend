"""Module for store api that relate to professor."""

from typing import Dict
from connexion.exceptions import ProblemException
from .models.profile_model import ProfessorConnections, Announcements, Profile
from .models.user_model import Professor, Company
from uuid import UUID


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
                session.query(Professor).where(Professor.user_id == user_uuid).one()
            )
            professor_connections = (
                session.query(ProfessorConnections)
                .where(ProfessorConnections.professor_id == professor.id)
                .all()
            )

            if not professor_connections:
                session.close()
                return []

            return [
                {
                    "id": conn.id,
                    "professor_id": conn.professor_id,
                    "company_id": conn.company_id,
                    "created_at": conn.created_at.isoformat()
                    if conn.created_at
                    else None,
                }
                for conn in professor_connections
            ]

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    def get_annoucement(self):
        """
        Return all announcements in the system.

        If `user_id` is provided it is ignored — the API returns all announcements.

        Each announcement will include the professor's
        first_name, last_name and profile_img if available.
        """
        session = self.db.get_session()
        try:
            announcements = session.query(Announcements).all()

            if not announcements:
                return []

            results = []
            for a in announcements:
                professor = (
                    session.query(Professor)
                    .where(Professor.id == a.professor_id)
                    .one_or_none()
                )

                prof_profile = None
                if professor:
                    prof_profile = (
                        session.query(Profile)
                        .where(Profile.user_id == professor.user_id)
                        .one_or_none()
                    )

                results.append(
                    {
                        "id": a.id,
                        "professor_id": a.professor_id,
                        "title": a.title,
                        "content": a.content,
                        "created_at": a.created_at.isoformat()
                        if a.created_at
                        else None,
                        "professor_first_name": prof_profile.first_name
                        if prof_profile
                        else None,
                        "professor_last_name": prof_profile.last_name
                        if prof_profile
                        else None,
                        "professor_profile_img": prof_profile.profile_img
                        if prof_profile
                        else None,
                    }
                )

            return results

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    def post_connection(self, user_id: str, body: dict):
        """
        Create a new connection for professor.

        Args:
            user_id: The unique ID of the user (string format).
            body: Dictionary containing company_id

        Returns:
            The connection dictionary with id, professor_id, company_id, created_at.
        """
        user_uuid = UUID(user_id)

        if not body:
            raise ProblemException("Request body cannot be empty.")

        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor)
                .where(Professor.user_id == user_uuid)
                .one_or_none()
            )

            if not professor:
                raise ProblemException(f"Professor with user_id '{user_id}' not found.")

            existing_connection = (
                session.query(ProfessorConnections)
                .where(
                    ProfessorConnections.professor_id == professor.id,
                    ProfessorConnections.company_id == body["company_id"],
                )
                .one_or_none()
            )

            if existing_connection:
                raise ProblemException(
                    f"Connection already exists between professor"
                    f" and company {body['company_id']}."
                )

            connection = ProfessorConnections(
                professor_id=professor.id, company_id=body["company_id"]
            )

            session.add(connection)
            session.commit()

            connection_data = {
                "id": connection.id,
                "professor_id": connection.professor_id,
                "company_id": connection.company_id,
                "created_at": connection.created_at.isoformat()
                if connection.created_at
                else None,
            }

            professor_profile = (
                session.query(Profile).where(Profile.user_id == user_uuid).one()
            )

            company = (
                session.query(Company)
                .where(
                    Company.id == connection.company_id,
                )
                .one()
            )

            company_profile = (
                session.query(Profile)
                .where(
                    Profile.user_id == company.user_id,
                )
                .one()
            )

            # create announcement using ORM attribute access
            annouce = Announcements(
                professor_id=connection_data["professor_id"],
                title=(
                    f"Professor {professor_profile.first_name}"
                    f" has connection with {company.company_name} company."
                ),
                content=company_profile.about,
            )

            session.add(annouce)
            session.commit()

            return connection_data

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    def delete_connection(self, user_id: str, connection_id: int) -> Dict:
        """
        Delete a connection for a professor.

        Corresponds to: DELETE /api/v1/connections/

        Args:
            user_id: The unique ID of the user (string format).
            connection_id: The unique ID of the connection to delete.

        Returns:
            A dictionary with success message.
        """
        user_uuid = UUID(user_id)
        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor)
                .where(Professor.user_id == user_uuid)
                .one_or_none()
            )

            if not professor:
                raise ProblemException(f"Professor with user_id '{user_id}' not found.")

            connection = (
                session.query(ProfessorConnections)
                .where(
                    ProfessorConnections.id == connection_id,
                    ProfessorConnections.professor_id == professor.id,
                )
                .one_or_none()
            )

            if not connection:
                # Single-line formatted message
                raise ProblemException(
                    f"Connection with id '{connection_id}'\
                      not found for this professor."
                )

            connection_data = {
                "id": connection.id,
                "professor_id": connection.professor_id,
                "company_id": connection.company_id,
                "created_at": connection.created_at.isoformat()
                if connection.created_at
                else None,
            }

            session.delete(connection)
            session.commit()

            return connection_data

        except ProblemException:
            session.rollback()
            raise
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error = {str(e)}")
        finally:
            session.close()
