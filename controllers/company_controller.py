"""Module for handing Job API path logic."""

import uuid

from typing import List, Dict
from .models.user_model import Company
from .models.profile_model import Profile
from .decorators import role_required
from .serialization import camelize
from swagger_server.openapi_server import models


class CompanyController:
    """Controller to use CRUD operations for Company."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    @role_required(["Student"])
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
                cdict = company.to_dict()

                profile = (
                    session.query(Profile)
                    .filter(Profile.user_id == company.user_id)
                    .one_or_none()
                )

                if profile:
                    cdict["profile"] = profile.to_dict()
                else:
                    cdict["profile"] = None

                company_data.append(cdict)

            session.close()
            return camelize(company_data), 200
        
        except Exception as e:
            session.close()
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400