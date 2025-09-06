"""Module for handing Job API path logic."""

from typing import List, Dict, Optional
from .db_controller import BaseController


class JobController(BaseController):
    """Controller to use CRUD operations for Job."""

    def __init__(self):
        """Initialize the class."""
        super().__init__()
    
    def get_all_jobs(self) -> List[Dict]:
        """
        Return all jobs in the jobs table.

        Retrieves all jobs from the MySQL database.
        Corresponds to: GET /api/v1/job/all
        """
        query = "SELECT * FROM Job;"
        try:
            return self.execute_query(query, fetchall=True)
        except Exception as e:
            return [{"error": f"Failed to fetch jobs: {str(e)}"}]
