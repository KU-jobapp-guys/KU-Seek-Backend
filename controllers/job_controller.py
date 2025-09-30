"""Module for handing Job API path logic."""

from typing import List, Dict
from .db_controller import BaseController
from flask import jsonify
from .models.job_model import Job, JobSkills, JobTags, JobApplication, Bookmark
from .models.user_model import Company
from .models.tag_term_model import Tags, Terms

class JobController(BaseController):
    """Controller to use CRUD operations for Job."""

    def __init__(self):
        """Initialize the class."""
        super().__init__()

    def get_all_jobs(self, job_id: str) -> List[Dict]:
        """
        Return all jobs in the jobs table if have job_id it will return only one job.
    
        Corresponds to: GET /api/v1/jobs

        Args:
            job_id: The unique ID of the job (string format).
        """
        try:
            session = self.get_session()
            if job_id:
                job = session.query(Job).where(
                    Job.id == job_id
                ).one_or_none()

                if not job:
                    session.close()
                    return []
            
                jobs = [job]

            else:
                jobs = session.query(Job).all()
            
            if not jobs:
                session.close()
                return []
            
            return self.__job_with_company_terms_tags(session, jobs)

                        
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
        Return filtered jobs from the jobs table using ORM.

        Corresponds to: POST /api/v1/jobs/search
        """
        try:
            session = self.get_session()
            
            query = session.query(Job).join(Company, Job.company_id == Company.id)
            
            for key, val in body.items():
                if key in ["skill_name", "tag_name"]:
                    continue
                
                elif key == "salary_min":
                    query = query.filter(Job.salary_min >= float(val))
                
                elif key == "salary_max":
                    query = query.filter(Job.salary_max <= float(val))
                
                elif key == "capacity":
                    query = query.filter(Job.capacity == int(val))
                
                elif key == "end_date":
                    query = query.filter(Job.end_date > val)
                
                elif key in ["company_name", "company_industry", "company_type"]:
                    query = query.filter(getattr(Company, key) == str(val))
                
                else:
                    query = query.filter(getattr(Job, key) == str(val))
            
            jobs = query.all()
            
            if not jobs:
                session.close()
                return [{"message": "No jobs found."}]
            
            return self.__job_with_company_terms_tags(session, jobs, body)
            
                        
        except Exception as e:
            return [{"error": str(e)}]

    def __job_with_company_terms_tags(self, session, jobs, body=None):
        """
        Return jobs data with company, terms, and tags.

        Corresponds to: The Job schema in the YAML file.
        """
        result = []
        for job in jobs:
            job_dict = job.to_dict()
            
            company = session.query(Company).filter(
                Company.id == job.company_id
            ).one_or_none()
            job_dict["company"] = company.to_dict() if company else None
            
            job_skills = session.query(JobSkills).filter(
                JobSkills.job_id == job.id
            ).all()
            
            skills_list = []
            for job_skill in job_skills:
                skill = session.query(Terms).filter(
                    Terms.id == job_skill.skill_id
                ).one_or_none()
                if skill:
                    skills_list.append(skill.to_dict())
            
            job_dict["skills"] = skills_list
            
            job_tags = session.query(JobTags).filter(
                JobTags.job_id == job.id
            ).all()
            
            tags_list = []
            for job_tag in job_tags:
                tag = session.query(Tags).filter(
                    Tags.id == job_tag.tag_id
                ).one_or_none()
                if tag:
                    tags_list.append(tag.to_dict())
            
            job_dict["tags"] = tags_list
            
            if body:
                if "skill_name" in body:
                    skill_names = [skill["name"] for skill in skills_list]
                    if body["skill_name"] not in skill_names:
                        continue
                
                if "tag_name" in body:
                    tag_names = [tag["name"] for tag in tags_list]
                    if body["tag_name"] not in tag_names:
                        continue
                
            result.append(job_dict)
        
        session.close()
        return result if result else [{"message": "No jobs found."}]