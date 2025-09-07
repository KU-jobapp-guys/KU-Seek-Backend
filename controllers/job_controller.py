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
        try:
            jobs_query = """
                SELECT Job.*, Company.*
                FROM Job
                LEFT JOIN Company ON Job.company_id = Company.id;
            """
            job_rows = self.execute_query(jobs_query, fetchall=True)


            skills_query = """
                SELECT js.job_id, t.id, t.name, t.type
                FROM Job_skills js
                JOIN Terms t ON js.skill_id = t.id;
            """
            skills_rows = self.execute_query(skills_query, fetchall=True)


            tags_query = """
                SELECT jt.job_id, t.id, t.name
                FROM Job_Tag jt
                JOIN Tags t ON jt.tag_id = t.id;
            """
            tags_rows = self.execute_query(tags_query, fetchall=True)

            company_columns = ['Company.id', 'user_id', 'company_name', 'company_type',
                            'company_industry', 'company_size', 'company_website',
                            'full_location']

            jobs = []
            for row in job_rows:
                job = dict(row)

                company = {col: job.pop(col) for col in company_columns if col in job}
                job['company'] = company

                job['skills'] = skills_rows

                job['tags'] = tags_rows

                jobs.append(job)

            return jobs if jobs else [{"message": "No jobs found."}]

        except Exception as e:
            return [{"error": str(e)}]
