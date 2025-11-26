"""Module for store api that relate to professor."""

from typing import Dict
from swagger_server.openapi_server import models
from .models.profile_model import ProfessorConnections, Profile, CompanyTags
from .models.user_model import Professor, Company
from .models.tag_term_model import Tags
from uuid import UUID
from .decorators import rate_limit, role_required
from logger.custom_logger import get_logger


logger = get_logger()


class ProfessorController:
    """Controller to use CRUD operations for operation that relate to Professor."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @rate_limit
    def get_connection(self, user_id: str):
        """
        Return all connections this Professor have.

        Corresponds to: GET /api/v1/connections

        Args:
            user_id: The unique ID of the user (string format).
        """
        try:
            user_uuid = UUID(user_id)
        except Exception:
            return models.ErrorMessage("Invalid user_id format. Expected UUID string."), 400

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

        except Exception as e:
            session.rollback()
            logger.exception("Database error getting connections: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            session.close()

    @rate_limit
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

        except Exception as e:
            session.rollback()
            logger.exception("Database error getting announcements: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            session.close()

    @role_required(["Professor"])
    @rate_limit
    def post_connection(self, user_id: str, body: dict):
        """
        Create a new connection for professor.

        Args:
            user_id: The unique ID of the user (string format).
            body: Dictionary containing company_id

        Returns:
            The connection dictionary with id, professor_id, company_id, created_at.
        """
        try:
            user_uuid = UUID(user_id)
        except Exception:
            return models.ErrorMessage("Invalid user_id format. Expected UUID string."), 400

        if not body:
            return models.ErrorMessage("Request body cannot be empty."), 400

        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor)
                .where(Professor.user_id == user_uuid)
                .one_or_none()
            )

            if not professor:
                session.close()
                return models.ErrorMessage("Professor not found"), 404

            existing_connection = (
                session.query(ProfessorConnections)
                .where(
                    ProfessorConnections.professor_id == professor.id,
                    ProfessorConnections.company_id == body["company_id"],
                )
                .one_or_none()
            )

            if existing_connection:
                session.close()
                return (
                    models.ErrorMessage(
                        f"Connection already exists between professor and company {body['company_id']}."
                    ),
                    409,
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
            session.close()
            return connection_data

        except Exception as e:
            session.rollback()
            logger.exception("Database error creating connection: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            try:
                session.close()
            except Exception:
                pass

    @role_required(["Professor"])
    @rate_limit
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
        try:
            user_uuid = UUID(user_id)
        except Exception:
            return models.ErrorMessage("Invalid user_id format. Expected UUID string."), 400

        session = self.db.get_session()
        try:
            professor = (
                session.query(Professor)
                .where(Professor.user_id == user_uuid)
                .one_or_none()
            )

            if not professor:
                session.close()
                return models.ErrorMessage("Professor not found"), 404

            connection = (
                session.query(ProfessorConnections)
                .where(
                    ProfessorConnections.id == connection_id,
                    ProfessorConnections.professor_id == professor.id,
                )
                .one_or_none()
            )

            if not connection:
                session.close()
                return (
                    models.ErrorMessage(
                        f"Connection with id '{connection_id}' not found for this professor."
                    ),
                    404,
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
            session.close()

            return connection_data

        except Exception as e:
            session.rollback()
            logger.exception("Database error deleting connection: %s", e)
            return models.ErrorMessage("Database Error"), 500
        finally:
            try:
                session.close()
            except Exception:
                pass
