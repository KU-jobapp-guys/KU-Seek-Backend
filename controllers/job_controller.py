"""Module for handing Job API path logic."""

from typing import List, Dict
from .db_controller import BaseController
from flask import jsonify
from .models.job_model import Job, JobSkills, JobTags, JobApplication, Bookmark
from .models.user_model import Company

class JobController(BaseController):
    """Controller to use CRUD operations for Job."""

    def __init__(self):
        """Initialize the class."""
        super().__init__()

    def get_all_jobs(self, job_id: str) -> List[Dict]:
        """
        Return all jobs in the jobs table.

        Corresponds to: GET /api/v1/jobs
        """
        if job_id:
            return self._get_jobs_with_filters({"id": job_id})
        try:

            session = self.get_session()
            jobs = session.query(Job).where(
            ).all()
            if not jobs:
                session.close()
                return
            jobs = jobs.to_dict()

            for job in jobs:
                company = session.query(Company).where(
                    Company
                ).one_or_none()
            session.close()
            return jobs
                    
        except Exception as e:
            return [{"error": str(e)}]

    def get_applied_jobs(self, user_id: str) -> List[Dict]:
        """
        Return applied jobs from the JobApplication table.

        Corresponds to: GET /api/v1/applications
        """
        try:

            session = self.get_session()
            user_jobapplications = session.query(JobApplication).where(
                JobApplication.student_id == user_id
            ).all()
            if not user_jobapplications:
                session.close()
                return
            user_jobapplications = user_jobapplications.to_dict()
            session.close()
            return user_jobapplications
                    
        except Exception as e:
            return [{"error": str(e)}]

    def get_bookmark_jobs(self, user_id: str) -> List[Dict]:
        """
        Return applied jobs from the Bookmarked table.

        Corresponds to: GET /api/v1/bookmarks
        """
        try:
            session = self.get_session()
            user_bookmarked_jobs = session.query(Bookmark).where(
                Bookmark.id == user_id
            ).all()
            if not user_bookmarked_jobs:
                session.close()
                return
            user_bookmarked_jobs = user_bookmarked_jobs.to_dict()
            session.close()
            return user_bookmarked_jobs

        except Exception as e:
            return [{"error": str(e)}]

    def get_filtered_job(self, body: Dict) -> List[Dict]:
        """
        Return filtered jobs from the jobs table.

        Corresponds to: POST /api/v1/jobs/search
        """
        return self._get_jobs_with_filters(body)

    def _get_jobs_with_filters(self, filters: Dict) -> List[Dict]:
        """
        Private method to get jobs with optional filters.

        For both get_all_jobs and get_filtered_job.
        """
        try:
            job_filters = {
                key: val
                for key, val in filters.items()
                if key not in ["skill_name", "tag_name"]
            }

            jobs_query, job_params = self._build_jobs_query(job_filters)
            job_rows = self.execute_query(jobs_query, job_params, fetchall=True)

            if not job_rows:
                return [{"message": "No jobs found."}]

            job_ids = [row["id"] for row in job_rows]

            skills_data = self._get_skills_for_jobs(job_ids)
            tags_data = self._get_tags_for_jobs(job_ids)

            jobs = self._assemble_job_results(job_rows, skills_data, tags_data)

            filtered_jobs = self._filter_jobs_by_skills_and_tags(jobs, filters)

            return filtered_jobs if filtered_jobs else [{"message": "No jobs found."}]

        except Exception as e:
            return [{"error": str(e)}]

    def _build_jobs_query(self, filters: Dict) -> tuple:
        """
        Build the main jobs query with WHERE conditions based on filters.

        Returns (query_string, parameters_list)
        """
        base_query = """
            SELECT Job.*, Company.*
            FROM Job
            LEFT JOIN Company ON Job.company_id = Company.id
        """

        where_conditions = []
        params = []

        for key, val in filters.items():
            if key == "salary_min":
                where_conditions.append("Job.salary_min >= %s")
                params.append(float(val))

            elif key == "salary_max":
                where_conditions.append("Job.salary_max <= %s")
                params.append(float(val))

            elif key == "capacity":
                where_conditions.append("Job.capacity = %s")
                params.append(int(val))

            elif key == "end_date":
                where_conditions.append("Job.end_date > %s")
                params.append(val)

            elif key in ["company_name", "company_industry", "company_type"]:
                where_conditions.append(f"Company.{key} = %s")
                params.append(str(val))

            else:
                # Assume it's a Job table column
                where_conditions.append(f"Job.{key} = %s")
                params.append(str(val))

        if where_conditions:
            query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
        else:
            query = base_query

        return query, params

    def _get_skills_for_jobs(self, job_ids: List[int]) -> Dict[int, List[Dict]]:
        """
        Get ALL skills for specific job IDs (no filtering).

        Returns dict mapping job_id to list of skills.
        """
        if not job_ids:
            return {}

        placeholders = ",".join(["%s"] * len(job_ids))
        query = f"""
            SELECT js.job_id, t.id, t.name, t.type
            FROM Job_skills js
            JOIN Terms t ON js.skill_id = t.id
            WHERE js.job_id IN ({placeholders})
        """

        skills_rows = self.execute_query(query, job_ids, fetchall=True)

        # Group by job_id
        skills_by_job = {}
        for row in skills_rows:
            job_id = row["job_id"]
            if job_id not in skills_by_job:
                skills_by_job[job_id] = []
            skills_by_job[job_id].append(
                {"id": row["id"], "name": row["name"], "type": row["type"]}
            )

        return skills_by_job

    def _get_tags_for_jobs(self, job_ids: List[int]) -> Dict[int, List[Dict]]:
        """
        Get ALL tags for specific job IDs (no filtering).

        Returns dict mapping job_id to list of tags.
        """
        if not job_ids:
            return {}

        placeholders = ",".join(["%s"] * len(job_ids))
        query = f"""
            SELECT jt.job_id, t.id, t.name
            FROM Job_Tag jt
            JOIN Tags t ON jt.tag_id = t.id
            WHERE jt.job_id IN ({placeholders})
        """

        tags_rows = self.execute_query(query, job_ids, fetchall=True)

        # Group by job_id
        tags_by_job = {}
        for row in tags_rows:
            job_id = row["job_id"]
            if job_id not in tags_by_job:
                tags_by_job[job_id] = []
            tags_by_job[job_id].append({"id": row["id"], "name": row["name"]})

        return tags_by_job

    def _assemble_job_results(
        self, job_rows: List[Dict], skills_data: Dict, tags_data: Dict
    ) -> List[Dict]:
        """Assemble the final job results with company, skills, and tags data."""
        company_columns = [
            "Company.id",
            "user_id",
            "company_name",
            "company_type",
            "company_industry",
            "company_size",
            "company_website",
            "full_location",
        ]

        jobs = []
        for row in job_rows:
            job = dict(row)
            job_id = job["id"]

            company = {
                col.replace("Company.", ""): job.pop(col, None)
                for col in company_columns
                if col in job
            }
            job["company"] = company

            job["skills"] = skills_data.get(job_id, [])
            job["tags"] = tags_data.get(job_id, [])

            jobs.append(job)

        return jobs

    def _filter_jobs_by_skills_and_tags(
        self, jobs: List[Dict], filters: Dict
    ) -> List[Dict]:
        """
        Filter jobs based on skill_name (skills) and tag_name after retrieving all data.

        Removes entire jobs that don't have matching skills or tags.
        """
        filtered_jobs = []

        for job in jobs:
            should_include = True

            if "skill_name" in filters:
                skill_name = filters["skill_name"]
                skill_names = [skill["name"] for skill in job.get("skills", [])]

                if skill_name not in skill_names:
                    should_include = False

            if "tag_name" in filters and should_include:
                tag_name = filters["tag_name"]
                tag_names = [tag["name"] for tag in job.get("tags", [])]

                if tag_name not in tag_names:
                    should_include = False

            if should_include:
                filtered_jobs.append(job)

        return filtered_jobs
