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
        Corresponds to: GET /api/v1/jobs
        """
        return self._get_jobs_with_filters({})


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
            jobs_query, job_params = self._build_jobs_query(filters)
            job_rows = self.execute_query(jobs_query, job_params, fetchall=True)

            if not job_rows:
                return [{"message": "No jobs found."}]

            # Get job IDs for filtering skills and tags
            job_ids = [row['id'] for row in job_rows]
            

            skills_data = self._get_skills_for_jobs(job_ids, filters)
            tags_data = self._get_tags_for_jobs(job_ids, filters)

            return self._assemble_job_results(job_rows, skills_data, tags_data)

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

            if key == 'salary_min':
                where_conditions.append("Job.salary_min >= %s")
                params.append(float(val))

            elif key == 'salary_max':
                where_conditions.append("Job.salary_max <= %s")
                params.append(float(val))

            elif key == 'capacity':
                where_conditions.append("Job.capacity = %s")
                params.append(int(val))

            elif key in ["company_name", "company_industry", "company_type"]:
                where_conditions.append(f"Company.{key} = %s")
                params.append(str(val))

            elif key in ["tag_name", "term_name"]:
                # We have seperate method to handle this. UwU
                continue
            else:
                where_conditions.append(f"Job.{key} = %s")
                params.append(str(val))
        
        if where_conditions:
            query = f"{base_query} WHERE {' AND '.join(where_conditions)}"
        else:
            query = base_query
            
        return query, params


    def _get_skills_for_jobs(self, job_ids: List[int], filters: Dict) -> Dict[int, List[Dict]]:
        """
        Get skills for specific job IDs, optionally filtered by term_name.
        Returns dict mapping job_id to list of skills.
        """
        if not job_ids:
            return {}
            
        placeholders = ','.join(['%s'] * len(job_ids))
        base_query = f"""
            SELECT js.job_id, t.id, t.name, t.type
            FROM Job_skills js
            JOIN Terms t ON js.skill_id = t.id
            WHERE js.job_id IN ({placeholders})
        """
        
        params = job_ids.copy()
        

        if 'term_name' in filters:
            base_query += " AND t.name = %s"
            params.append(str(filters['term_name']))
        
        skills_rows = self.execute_query(base_query, params, fetchall=True)
        
        # Group by job_id
        skills_by_job = {}
        for row in skills_rows:
            job_id = row['job_id']
            if job_id not in skills_by_job:
                skills_by_job[job_id] = []
            skills_by_job[job_id].append({
                'id': row['id'],
                'name': row['name'],
                'type': row['type']
            })
        
        return skills_by_job


    def _get_tags_for_jobs(self, job_ids: List[int], filters: Dict) -> Dict[int, List[Dict]]:
        """
        Get tags for specific job IDs, optionally filtered by tag_name.
        Returns dict mapping job_id to list of tags.
        """
        if not job_ids:
            return {}
            
        placeholders = ','.join(['%s'] * len(job_ids))
        base_query = f"""
            SELECT jt.job_id, t.id, t.name
            FROM Job_Tag jt
            JOIN Tags t ON jt.tag_id = t.id
            WHERE jt.job_id IN ({placeholders})
        """
        
        params = job_ids.copy()
        

        if 'tag_name' in filters:
            base_query += " AND t.name = %s"
            params.append(str(filters['tag_name']))
        
        tags_rows = self.execute_query(base_query, params, fetchall=True)
        
        # Group by job_id
        tags_by_job = {}
        for row in tags_rows:
            job_id = row['job_id']
            if job_id not in tags_by_job:
                tags_by_job[job_id] = []
            tags_by_job[job_id].append({
                'id': row['id'],
                'name': row['name']
            })
        
        return tags_by_job


    def _assemble_job_results(self, job_rows: List[Dict], skills_data: Dict, tags_data: Dict) -> List[Dict]:
        """
        Assemble the final job results with company, skills, and tags data.
        """
        company_columns = ['Company.id', 'user_id', 'company_name', 'company_type',
                        'company_industry', 'company_size', 'company_website',
                        'full_location']
        
        jobs = []
        for row in job_rows:
            job = dict(row)
            job_id = job['id']
            
            # Extract company data
            company = {col.replace('Company.', ''): job.pop(col, None) 
                    for col in company_columns if col in job}
            job['company'] = company
            
            # Add skills and tags for this job
            job['skills'] = skills_data.get(job_id, [])
            job['tags'] = tags_data.get(job_id, [])
            
            jobs.append(job)
        
        return jobs