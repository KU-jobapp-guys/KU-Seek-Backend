"""Module for handing Job API path logic."""

from typing import List, Dict
import uuid
from .models.user_model import Company
from .models.job_model import Job
from .models.profile_model import Profile
from swagger_server.openapi_server import models
from .decorators import login_required


class CompanyController:
    """Controller to use CRUD operations for Company."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @login_required
    def get_company(self, user_id: str) -> Dict:
        """
        Return company data for the company associated with the given user id.

        Args:
            user_id: the authenticated user's id (from JWT)

        Returns:
            A dict shaped for the frontend (CompanyProfile) and status code tuple.
        """
        session = self.db.get_session()
        try:
            if isinstance(user_id, dict):
                session.close()
                return {"message": "Invalid user id in token"}, 400

            query_user_id = user_id
            if isinstance(user_id, str):
                try:
                    query_user_id = uuid.UUID(user_id)
                except Exception:
                    query_user_id = user_id

            company = (
                session.query(Company)
                .where(Company.user_id == query_user_id)
                .one_or_none()
            )
            if not company:
                session.close()
                return models.ErrorMessage("Company not found"), 404

            profile = (
                session.query(Profile)
                .filter(Profile.user_id == company.user_id)
                .one_or_none()
            )

            pr = profile.to_dict() if profile else {}

            job_count = session.query(Job).filter(Job.company_id == company.id).count()

            mapped = {
                "userId": str(company.user_id),
                "companyId": str(company.id),
                "companyName": company.company_name or "",
                "jobCount": job_count,
                "profilePhoto": pr.get("profile_img") or "",
                "bannerPhoto": pr.get("banner_img") or "",
                "industry": company.company_industry,
                "location": pr.get("location") or "",
            }

            session.close()
            return mapped, 200

        except Exception as e:
            session.close()
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400

    @login_required
    def get_all_companies(self) -> List[Dict]:
        """
        Return all company in companies table.

        Corresponds to: GET /api/v1/companies
        """
        session = self.db.get_session()
        try:
            companies = session.query(Company).all()
            if not companies:
                session.close()
                return []

            company_data = []
            for company in companies:
                profile = (
                    session.query(Profile)
                    .filter(Profile.user_id == company.user_id)
                    .one_or_none()
                )

                job_count = (
                    session.query(Job).filter(Job.company_id == company.id).count()
                )

                pr = profile.to_dict() if profile else {}

                mapped = {
                    "userId": str(company.user_id),
                    "companyId": str(company.id),
                    "companyName": company.company_name or "",
                    "jobCount": job_count,
                    "profilePhoto": pr.get("profile_img") or "",
                    "bannerPhoto": pr.get("banner_img") or "",
                    "industry": company.company_industry,
                    "location": pr.get("location") or "",
                }

                company_data.append(mapped)

            session.close()
            return company_data, 200

        except Exception as e:
            session.close()
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400
