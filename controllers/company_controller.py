"""Module for handing Job API path logic."""

from typing import List, Dict
from .models.user_model import Company
from .models.job_model import Job
from .models.profile_model import Profile
from .decorators import role_required
from swagger_server.openapi_server import models


class CompanyController:
    """Controller to use CRUD operations for Company."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

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
                    session.query(Job)
                    .filter(Job.company_id == company.id)
                    .count()
                )

                pr = profile.to_dict() if profile else {}

                mapped = {
                    "companyId": str(company.id),
                    "companyName": company.company_name or "",
                    "jobCount": job_count,
                    "profilePhoto": pr.get("profile_img") or "",
                }

                company_data.append(mapped)

            session.close()
            return company_data, 200
        
        except Exception as e:
            session.close()
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400
        