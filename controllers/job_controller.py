"""Module for handing Job API path logic."""

import uuid

from typing import List, Dict
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from .models.job_model import Job, JobSkills, JobTags, Bookmark, JobApplication
from .models.user_model import Company, Student
from .models.tag_term_model import Tags, Terms


class JobController:
    """Controller to use CRUD operations for Job."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database

    def get_all_jobs(self, job_id: str) -> List[Dict]:
        """
        Return all jobs in the jobs table if have job_id it will return only one job.

        Corresponds to: GET /api/v1/jobs

        Args:
            job_id: The unique ID of the job (string format).
        """
        session = self.db.get_session()
        try:
            if job_id:
                job = session.query(Job).where(Job.id == job_id).one_or_none()
                if not job:
                    session.close()
                    return []
                jobs = [job]
                return self.__job_with_company_terms_tags(
                    session, jobs, single_response=True
                )
            else:
                jobs = session.query(Job).all()
                if not jobs:
                    session.close()
                    return []
                return self.__job_with_company_terms_tags(session, jobs)
        except Exception as e:
            session.close()
            raise Exception(f"Error retrieving jobs: {str(e)}")

    def post_job(self, user_id: str, body: Dict) -> Dict:
        """
        Create a new Job from the request body.

        Creates a new job and inserts it into the MySQL database.
        Corresponds to: POST /api/v1/jobs

        Args:
            body: A request body containing job information with required fields:
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
                                - skill_names (list[str]): List of skill names (strings)
                                - tag_names (list[str]): List of tag names (strings)
                                    If a name does not exist in Tags it will be created

        Returns:
            Dict: The created job data

        Raises:
            ValueError: If required fields are missing or invalid
        """
        required_fields = [
            "title",
            "salary_min",
            "salary_max",
            "location",
            "work_hours",
            "job_type",
            "job_level",
            "capacity",
            "end_date",
        ]

        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        session = self.db.get_session()

        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format. Expected UUID string.")

        try:
            end_date = body["end_date"]
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

            company_obj = (
                session.query(Company).where(Company.user_id == user_id).one_or_none()
            )

            if not company_obj:
                raise ValueError(
                    "Company not found for current user. Create a company first."
                )

            job = Job(
                company_id=company_obj.id,
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
                status="pending",
            )

            session.add(job)
            session.flush()

            if "skill_names" in body and body["skill_names"]:
                if not isinstance(body["skill_names"], list):
                    raise ValueError("skill_names must be an array of strings")
                for name in body["skill_names"]:
                    if not name:
                        continue
                    name = str(name).strip()
                    term = session.query(Terms).where(Terms.name == name).one_or_none()
                    if not term:
                        raise ValueError(f"Term not found: {name}")
                    job_skill = JobSkills(job_id=job.id, skill_id=term.id)
                    session.add(job_skill)

            if "tag_names" in body and body["tag_names"]:
                if not isinstance(body["tag_names"], list):
                    raise ValueError("tag_names must be an array of strings")
                for name in body["tag_names"]:
                    if not name:
                        continue
                    tag_id = self._get_or_create_tag(session, str(name).strip())
                    job_tag = JobTags(job_id=job.id, tag_id=tag_id)
                    session.add(job_tag)

            session.commit()

            # Return the created job with relationships
            jobs = [job]
            return self.__job_with_company_terms_tags(
                session, jobs, single_response=True
            )

        except IntegrityError as e:
            session.rollback()
            session.close()
            raise ValueError(f"Invalid foreign key reference: {str(e)}")
        except Exception as e:
            session.rollback()
            session.close()
            raise Exception(f"Error creating job: {str(e)}")

    def get_bookmark_jobs(self, user_id: str) -> List[Dict]:
        """
        Return bookmarked job from the Bookmarked table.

        Corresponds to: GET /api/v1/bookmarks
        """
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format. Expected UUID string.")

        session = self.db.get_session()
        try:
            student = (
                session.query(Student).where(Student.user_id == user_id).one_or_none()
            )

            user_bookmarked_jobs = (
                session.query(Bookmark).where(Bookmark.student_id == student.id).all()
            )

            if not user_bookmarked_jobs:
                session.close()
                return []

            result = [bookmark.to_dict() for bookmark in user_bookmarked_jobs]
            session.close()
            return result
        except Exception as e:
            session.close()
            raise Exception(f"Error retrieving bookmarked jobs: {str(e)}")

    def post_bookmark_jobs(self, user_id, body: Dict) -> Dict:
        """
        Post bookmarked job from the Bookmarked table.

        Corresponds to: POST /api/v1/bookmarks
        """
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format. Expected UUID string.")

        for key in body.keys():
            if key != "job_id":
                raise ValueError(f"Cannot filter by these keys: {key}")

        session = self.db.get_session()

        student = session.query(Student).where(Student.user_id == user_id).one_or_none()

        try:
            bookmark = Bookmark(job_id=body["job_id"], student_id=student.id)

            session.add(bookmark)

            session.commit()

            result = {
                "id": bookmark.id,
                "job_id": bookmark.job_id,
                "student_id": bookmark.student_id,
                "created_at": bookmark.created_at.isoformat()
                if bookmark.created_at
                else None,
            }

            session.close()

            return result

        except Exception as e:
            session.close()
            raise Exception(f"Error retrieving bookmarked jobs: {str(e)}")

    def delete_bookmark_jobs(self, user_id, job_id: int) -> Dict:
        """
        Delete bookmarked job from the Bookmarked table.

        Corresponds to: DELETE /api/v1/bookmarks
        """
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format. Expected UUID string.")

        session = self.db.get_session()

        try:
            student = (
                session.query(Student).where(Student.user_id == user_id).one_or_none()
            )

            if not student:
                session.close()
                raise ValueError("Student not found")

            bookmark = (
                session.query(Bookmark)
                .where(Bookmark.job_id == job_id, Bookmark.student_id == student.id)
                .one_or_none()
            )

            if not bookmark:
                session.close()
                raise ValueError("Bookmark not found")
            result = {
                "id": bookmark.id,
                "job_id": bookmark.job_id,
                "student_id": bookmark.student_id,
                "created_at": bookmark.created_at.isoformat()
                if bookmark.created_at
                else None,
            }

            session.delete(bookmark)

            session.commit()

            session.close()

            return result

        except Exception as e:
            session.rollback()
            session.close()
            raise Exception(f"Error deleting bookmark: {str(e)}")

    def get_filtered_job(self, body: Dict) -> List[Dict]:
        """
        Return filtered jobs from the jobs table using ORM.

        Corresponds to: POST /api/v1/jobs/search

        Args:
            body: Filter criteria including:
                - skill_names (list[str]): List of skill names
                - tag_names (list[str]): List of tag names
                - Other job fields for filtering
        """
        allowed_job_fields = {
            "title",
            "salary_min",
            "salary_max",
            "location",
            "work_hours",
            "job_type",
            "job_level",
            "capacity",
            "end_date",
        }
        allowed_company_fields = {
            "company_name",
            "company_industry",
            "company_type",
            "user_id",
        }
        allowed_special_fields = {"skill_names", "tag_names"}

        all_allowed_fields = (
            allowed_job_fields | allowed_company_fields | allowed_special_fields
        )

        def _is_empty_filter(d: Dict) -> bool:
            if not d:
                return True
            for v in d.values():
                if v is None or v == "":
                    continue
                if isinstance(v, list) and len(v) == 0:
                    continue
                return False
            return True

        if _is_empty_filter(body):
            return self.get_all_jobs("")

        session = self.db.get_session()

        try:
            # Validate filter keys
            invalid_keys = [key for key in body.keys() if key not in all_allowed_fields]
            if invalid_keys:
                session.close()
                raise ValueError(
                    f"Cannot filter by these keys: {', '.join(invalid_keys)}"
                )

            query = session.query(Job).join(Company, Job.company_id == Company.id)

            owner_user_id = body.pop("user_id", None)
            if owner_user_id:
                try:
                    # Accept UUID string or UUID instance
                    if isinstance(owner_user_id, str):
                        from uuid import UUID as _UUID

                        owner_uuid = _UUID(owner_user_id)
                    else:
                        owner_uuid = owner_user_id
                except Exception:
                    session.close()
                    raise ValueError("Invalid user_id format. Expected UUID string.")
                company_obj = (
                    session.query(Company)
                    .where(Company.user_id == owner_uuid)
                    .one_or_none()
                )
                if not company_obj:
                    session.close()
                    raise ValueError("Company not found for provided user_id")

                query = query.filter(Job.company_id == company_obj.id)

            skill_names = body.pop("skill_names", None)
            tag_names = body.pop("tag_names", None)

            # Apply basic filters
            for key, val in body.items():
                if val is None or val == "":
                    continue

                if key == "salary_min":
                    try:
                        query = query.filter(Job.salary_min >= float(val))
                    except (ValueError, TypeError):
                        session.close()
                        raise ValueError(f"Invalid value for salary_min: {val}")

                elif key == "salary_max":
                    try:
                        query = query.filter(Job.salary_max <= float(val))
                    except (ValueError, TypeError):
                        session.close()
                        raise ValueError(f"Invalid value for salary_max: {val}")

                elif key == "capacity":
                    try:
                        query = query.filter(Job.capacity == int(val))
                    except (ValueError, TypeError):
                        session.close()
                        raise ValueError(f"Invalid value for capacity: {val}")

                elif key == "end_date":
                    try:
                        end_date = val
                        if isinstance(end_date, str):
                            end_date = datetime.fromisoformat(
                                end_date.replace("Z", "+00:00")
                            )
                        query = query.filter(Job.end_date >= end_date)
                    except (ValueError, TypeError):
                        session.close()
                        raise ValueError(f"Invalid date format for end_date: {val}")

                elif key in allowed_company_fields:
                    query = query.filter(getattr(Company, key).ilike(f"%{val}%"))

                elif key in allowed_job_fields:
                    if key == "location":
                        from sqlalchemy import or_

                        query = query.filter(
                            or_(
                                Job.location.ilike(f"%{val}%"),
                                Company.full_location.ilike(f"%{val}%"),
                            )
                        )
                    else:
                        query = query.filter(getattr(Job, key).ilike(f"%{val}%"))

            # Filter by skills if provided
            if skill_names:
                if not isinstance(skill_names, list):
                    session.close()
                    raise ValueError("skill_names must be an array")

                if len(skill_names) > 0:
                    skill_job_ids = (
                        session.query(JobSkills.job_id)
                        .join(Terms, JobSkills.skill_id == Terms.id)
                        .filter(Terms.name.in_(skill_names))
                        .distinct()
                    )
                    query = query.filter(Job.id.in_(skill_job_ids))

            # Filter by tags if provided
            if tag_names:
                if not isinstance(tag_names, list):
                    session.close()
                    raise ValueError("tag_names must be an array")

                if len(tag_names) > 0:
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

        except ValueError:
            raise
        except Exception as e:
            session.close()
            raise Exception(f"Error filtering jobs: {str(e)}")

    def __job_with_company_terms_tags(self, session, jobs, single_response=None):
        """Return jobs data shaped for the frontend.

        Produces objects like the provided frontend mock where:
        - jobId: string representation of the job id
        - company: company name string
        - role: job title
        - jobLevel: job_level
        - location: company.full_location or job.location
        - postTime: ISO timestamp string (frontend will parse to Date)
        - skills: list[str] of term names
        - tags: list[str] of tag names (optional)
        - pendingApplicants / totalApplicants computed from JobApplication rows
                - contacts: list of contact objects derived from
                    company.company_website when present
        """
        result = []
        for job in jobs:
            company = (
                session.query(Company)
                .filter(Company.id == job.company_id)
                .one_or_none()
            )

            company_name = company.company_name if company else None

            location = job.location or company.full_location

            job_skills = (
                session.query(JobSkills).filter(JobSkills.job_id == job.id).all()
            )
            skills_list = []
            for job_skill in job_skills:
                skill = (
                    session.query(Terms)
                    .filter(Terms.id == job_skill.skill_id)
                    .one_or_none()
                )
                if skill:
                    skills_list.append(skill.name)

            job_tags = session.query(JobTags).filter(JobTags.job_id == job.id).all()
            tags_list = []
            for job_tag in job_tags:
                tag = (
                    session.query(Tags).filter(Tags.id == job_tag.tag_id).one_or_none()
                )
                if tag:
                    tags_list.append(tag.name)

            try:
                total_applicants = (
                    session.query(JobApplication)
                    .filter(JobApplication.job_id == job.id)
                    .count()
                )
                pending_applicants = (
                    session.query(JobApplication)
                    .filter(
                        JobApplication.job_id == job.id,
                        JobApplication.status == "pending",
                    )
                    .count()
                )
            except Exception:
                total_applicants = 0
                pending_applicants = 0

            contacts = []
            if company and company.company_website:
                link = company.company_website
                contact_type = "email" if "@" in link else "website"
                contacts.append({"type": contact_type, "link": link})

            post_time = (
                job.created_at.isoformat() if getattr(job, "created_at", None) else None
            )

            job_id_slug = str(job.id)

            mapped = {
                "jobId": job_id_slug,
                "company": company_name,
                "role": job.title,
                "jobLevel": job.job_level,
                "location": location,
                "postTime": post_time,
                "description": job.description,
                "jobType": job.job_type,
                "skills": skills_list,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "status": job.status,
                "pendingApplicants": pending_applicants,
                "totalApplicants": total_applicants,
            }

            if contacts:
                mapped["contacts"] = contacts

            if tags_list:
                mapped["tags"] = tags_list

            result.append(mapped)

        session.close()

        if single_response and result:
            return result[0]
        return result

    def _get_or_create_tag(self, session, name: str) -> int:
        """Return tag id for name, creating the tag if it doesn't exist.

        Uses the provided session and handles race conditions similarly to terms.
        """
        try:
            tag = session.query(Tags).where(Tags.name == name).one_or_none()
            if tag:
                return tag.id

            tag = Tags(name=name)
            session.add(tag)
            try:
                session.flush()
                return tag.id
            except IntegrityError:
                session.rollback()
                tag = session.query(Tags).where(Tags.name == name).one()
                return tag.id
        except Exception:
            session.rollback()
            raise
