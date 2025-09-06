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
        Corresponds to: GET /api/v1/jobs
        """
        query = "SELECT * FROM Job;"
        return self.execute_query(query, fetchall=True)
