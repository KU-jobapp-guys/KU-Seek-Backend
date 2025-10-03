"""Module for handing Job API path logic."""

from typing import List, Dict
from .db_controller import BaseController
from datetime import datetime
from sqlalchemy.exc import IntegrityError
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

                return self.__job_with_company_terms_tags(session, jobs, single_response=True)


            else:
                jobs = session.query(Job).all()
            
            if not jobs:
                session.close()
                return []
            
            return self.__job_with_company_terms_tags(session, jobs)

                        
        except Exception as e:
            return [{"error": str(e)}]
    
    def post_job(self, body: Dict) -> Dict:
        """
        Create a new Job from the request body.

        Creates a new job and inserts it into the MySQL database.
        Corresponds to: POST /api/v1/jobs

        Args:
            body: A request body containing job information with required fields:
                - company_id (int): ID of the company posting the job
                - title (str): Job title
                - salary_min (float): Minimum salary
                - salary_max (float): Maximum salary
                - location (str): Job location
                - work_hours (str): Working hours
                - job_type (str): Type of job
                - job_level (str): Level of job
                - capacity (int): Number of positions
                - end_date (str): Application deadline (ISO format)
                
            Optional fields:
                - description (str): Job description
                - visibility (bool): Whether job is visible
                - skill_ids (list[int]): List of skill IDs
                - tag_ids (list[int]): List of tag IDs

        Returns:
            Dict: The created job data

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = [
            "company_id", "title", "salary_min", "salary_max",
            "location", "work_hours", "job_type", "job_level",
            "capacity", "end_date"
        ]
        
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        session = self.get_session()
        
        try:
            end_date = body["end_date"]
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            job = Job(
                company_id=body["company_id"],
                title=body["title"],
                description=body.get("description"),
                salary_min=body["salary_min"],
                salary_max=body["salary_max"],
                location=body["location"],
                work_hours=body["work_hours"],
                job_type=body["job_type"],
                job_level=body["job_level"],
                capacity=body["capacity"],
                end_date=end_date,
                visibility=body.get("visibility", False),
                status="pending"  
            )
            
            session.add(job)
            session.flush()  # Get the job.id before commit
            
            # Add skills if provided
            if "skill_ids" in body and body["skill_ids"]:
                for skill_id in body["skill_ids"]:
                    job_skill = JobSkills(job_id=job.id, skill_id=skill_id)
                    session.add(job_skill)
            
            # Add tags if provided
            if "tag_ids" in body and body["tag_ids"]:
                for tag_id in body["tag_ids"]:
                    job_tag = JobTags(job_id=job.id, tag_id=tag_id)
                    session.add(job_tag)
            
            session.commit()
            
            new_job = job.to_dict()
            
            return new_job
            
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Invalid foreign key reference: {str(e)}")
        except Exception as e:
            session.rollback()
            raise ValueError(f"Error creating job: {str(e)}")
        finally:
            session.close()

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
        
        Args:
            body: Filter criteria including:
                - skill_names (list[str]): List of skill names (e.g., ["React", "Python"])
                - tag_names (list[str]): List of tag names (e.g., ["Remote Work"])
                - Other job fields for filtering
        """
        try:
            session = self.get_session()
            
            query = session.query(Job).join(Company, Job.company_id == Company.id)
            
            skill_names = body.pop("skill_names", None)
            tag_names = body.pop("tag_names", None)
            
            for key, val in body.items():
                if key == "salary_min":
                    query = query.filter(Job.salary_min >= float(val))
                
                elif key == "salary_max":
                    query = query.filter(Job.salary_max <= float(val))
                
                elif key == "capacity":
                    query = query.filter(Job.capacity == int(val))
                
                elif key == "end_date":
                    end_date = val
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    query = query.filter(Job.end_date >= end_date)
                
                elif key in ["company_name", "company_industry", "company_type"]:
                    query = query.filter(getattr(Company, key).ilike(f"%{val}%"))
                
                else:
                    if hasattr(Job, key):
                        query = query.filter(getattr(Job, key).ilike(f"%{val}%"))
            
            if skill_names and isinstance(skill_names, list) and len(skill_names) > 0:

                skill_job_ids = (
                    session.query(JobSkills.job_id)
                    .join(Terms, JobSkills.skill_id == Terms.id)
                    .filter(Terms.name.in_(skill_names))
                    .distinct()
                )
                query = query.filter(Job.id.in_(skill_job_ids))
            

            if tag_names and isinstance(tag_names, list) and len(tag_names) > 0:

                tag_job_ids = (
                    session.query(JobTags.job_id)
                    .join(Tags, JobTags.tag_id == Tags.id)
                    .filter(Tags.name.in_(tag_names))
                    .distinct()
                )
                query = query.filter(Job.id.in_(tag_job_ids))
            
            jobs = query.all()
            
            if not jobs:
                session.close()
                return []
            
            return self.__job_with_company_terms_tags(session, jobs)
            
        except Exception as e:
            if session:
                session.close()
            return [{"error": str(e)}]

    def __job_with_company_terms_tags(self, session, jobs,
                                       single_response=None, body=None):
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
        
        if result and single_response:
            return result[0]
        elif result:
            return result
        else:
            return [{"message": "No jobs found."}]