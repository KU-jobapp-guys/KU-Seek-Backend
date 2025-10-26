"""Module for store api that relate to professor."""

from typing import Dict
from connexion.exceptions import ProblemException
from .models.profile_model import ProfessorConnections, Profile, CompanyTags
from .models.user_model import Professor, Company
from .models.tag_term_model import Tags
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
            connections = session.query(ProfessorConnections).all()

            if not connections:
                return []

            results = []
            for c in connections:
                professor = (
                    session.query(Professor)
                    .where(Professor.id == c.professor_id)
                    .one_or_none()
                )

                prof_profile = None
                if professor:
                    prof_profile = (
                        session.query(Profile)
                        .where(Profile.user_id == professor.user_id)
                        .one_or_none()
                    )

                company = (
                    session.query(Company)
                    .where(Company.id == c.company_id)
                    .one_or_none()
                )

                tags = []
                if company:
                    tag_rows = (
                        session.query(Tags)
                        .join(CompanyTags, CompanyTags.tag_id == Tags.id)
                        .filter(CompanyTags.company_id == company.id)
                        .all()
                    )
                    tags = [t.name for t in tag_rows if t and t.name]

                results.append(
                    {
                        "id": c.id,
                        "professor": (
                            (
                                (
                                    (prof_profile.first_name or "")
                                    + " "
                                    + (prof_profile.last_name or "")
                                ).strip()
                            )
                            if prof_profile
                            else None
                        ),
                        "professorPosition": professor.position if professor else None,
                        "department": professor.department if professor else None,
                        "company": company.company_name if company else None,
                        "companyIndustry": (
                            company.company_industry if company else None
                        ),
                        "tags": tags,
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
