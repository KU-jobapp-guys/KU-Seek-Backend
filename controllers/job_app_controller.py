"""Module containing endpoints for job applications."""

import os
from typing import Dict
from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config, Csv
from sqlalchemy.orm import joinedload
from swagger_server.openapi_server import models
from werkzeug.utils import secure_filename
from .models.job_model import Job, JobApplication
from .models.user_model import Student, Company
from .models.file_model import File


ALLOWED_FILE_FORMATS = config(
    "ALLOWED_FILE_FORMATS", cast=Csv(), default="application/pdf, application/msword"
)
BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")
VALID_STATUSES = ["accepted", "rejected"]


class JobApplicationController:
    """Controller for handling job application operations."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    @role_required(["Student"])
    def create_job_application(self, body, job_id: int):
        """Create a new job application from the request body."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        form = request.form
        session = self.db.get_session()

        job = session.query(Job).where(Job.id == job_id).one_or_none()
        current_applicants = (
            session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        student = (
            session.query(Student)
            .where(Student.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not student:
            session.close()
            return models.ErrorMessage("Student not found"), 400

        if not job:
            session.close()
            return models.ErrorMessage("Job not found."), 400

        if not len(current_applicants) < job.capacity:
            session.close()
            return models.ErrorMessage("Invalid job provided."), 400

        if str(student.id) in [
            str(applicant.student_id) for applicant in current_applicants
        ]:
            session.close()
            return models.ErrorMessage("Could not create job application."), 400

        # handle fields

        job_application = JobApplication(
            job_id=job_id,
            student_id=student.id,
            first_name=form.get("first_name"),
            last_name=form.get("last_name"),
            contact_email=form.get("email"),
            years_of_experience=form.get("years_of_experience"),
            expected_salary=form.get("expected_salary"),
            phone_number=form.get("phone_number"),
        )

        base_path = os.path.join(os.getcwd(), BASE_FILE_PATH)

        # process application letter
        letter = request.files.get("application_letter")
        if not letter:
            session.close()
            return models.ErrorMessage("Missing required application letter file"), 400

        if letter.content_type not in ALLOWED_FILE_FORMATS:
            session.close()
            return models.ErrorMessage("Invalid letter file type provided"), 400

        letter_file_name = secure_filename(letter.filename)
        letter_file_path = base_path + "/" + letter_file_name

        letter_model = File(
            owner=UUID(token_info["uid"]),
            file_name=letter_file_name,
            file_path=BASE_FILE_PATH + "/" + letter_file_name,
            file_type="letter",
        )

        # check if resume is an ID
        resume = form.get("resume")
        if resume:
            session.add(letter_model)
            session.commit()

            session.refresh(letter_model)
            job_application.resume = resume
            job_application.letter_of_application = letter_model.id
            session.add(job_application)
            session.commit()

            job_app_data = job_application.to_dict()
            session.close()

            return job_app_data, 200

        # process resume
        resume = request.files.get("resume")
        if not resume:
            session.close()
            return models.ErrorMessage("Missing required resume file"), 400

        if resume.content_type not in ALLOWED_FILE_FORMATS:
            session.close()
            return models.ErrorMessage("Invalid resume file type provided"), 400

        resume_file_name = secure_filename(resume.filename)
        resume_file_path = base_path + "/" + resume_file_name

        resume_model = File(
            owner=UUID(token_info["uid"]),
            file_name=resume_file_name,
            file_path=BASE_FILE_PATH + "/" + resume_file_name,
            file_type="resume",
        )

        # commit transaction
        resume.save(resume_file_path)
        letter.save(letter_file_path)
        session.add_all([letter_model, resume_model])
        session.commit()

        # update job application with the file ids
        session.refresh(letter_model)
        session.refresh(resume_model)
        job_application.resume = resume_model.id
        job_application.letter_of_application = letter_model.id

        session.add(job_application)
        session.commit()

        job_app_data = job_application.to_dict()
        session.close()

        return job_app_data, 200

    @role_required(["Student"])
    def fetch_user_job_applications(self):
        """Fetch all job applications belonging to the owner."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        student = (
            session.query(Student)
            .where(Student.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not student:
            session.close()
            return models.ErrorMessage("Student not found"), 400

        job_apps = (
            session.query(JobApplication)
            .options(joinedload(JobApplication.job))
            .where(JobApplication.student_id == student.id)
            .all()
        )

        formatted_apps = [
            models.JobApplication(
                applicant={
                    "user_id": str(j_app.student_id),
                    "first_name": j_app.first_name,
                    "last_name": j_app.last_name,
                    "contact_email": j_app.contact_email,
                },
                job_details={
                    "job_id": str(j_app.job.id),
                    "job_title": j_app.job.title,
                },
                resume=j_app.resume,
                letter_of_application=j_app.letter_of_application,
                years_of_experience=j_app.years_of_experience,
                expected_salary=j_app.expected_salary,
                phone_number=j_app.phone_number,
                status=j_app.status,
                applied_at=j_app.applied_at,
            )
            for j_app in job_apps
        ]

        session.close()

        return formatted_apps, 200

    @role_required(["Company"])
    def fetch_job_application_from_job_post(self, job_id: int):
        """Fetch all job applications for a specific job post."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        company = (
            session.query(Company)
            .where(Company.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not company:
            session.close()
            return models.ErrorMessage("Company not found"), 400

        job = session.query(Job).where(Job.id == job_id).one_or_none()

        if not job:
            session.close()
            return models.ErrorMessage("Invalid job provided"), 400

        if job.company_id != company.id:
            session.close()
            return models.ErrorMessage("User is not the job owner"), 403

        job_apps = (
            session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        formatted_apps = [
            models.JobApplication(
                applicant={
                    "user_id": str(j_app.student_id),
                    "first_name": j_app.first_name,
                    "last_name": j_app.last_name,
                    "contact_email": j_app.contact_email,
                },
                resume=j_app.resume,
                letter_of_application=j_app.letter_of_application,
                years_of_experience=j_app.years_of_experience,
                expected_salary=j_app.expected_salary,
                phone_number=j_app.phone_number,
                status=j_app.status,
                applied_at=j_app.applied_at,
            )
            for j_app in job_apps
        ]

        session.close()

        return formatted_apps, 200

    @role_required(["Company"])
    def update_job_applications_status(self, job_id: int, body: list[Dict]):
        """
        Update the status of multiple job applications.

        Update the status of all job applications sent in the request body,
        and queues an email notifying students about their job application
        status.

        Args:
            job_id: The job id for the job application's applied job
            body: The request body, in the format of a list of JSON
                  with the following attribues:
                    {application_id: str, status: str}

        returns A copy of a list of updated job applications
        """
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        if not body:
            return models.ErrorMessage("No job applications provided"), 400

        session = self.db.get_session()

        company = (
            session.query(Company)
            .where(Company.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not company:
            session.close()
            return models.ErrorMessage("Company not found"), 400

        job = session.query(Job).where(Job.id == job_id).one_or_none()

        if not job:
            session.close()
            return models.ErrorMessage("Invalid job provided"), 400

        if job.company_id != company.id:
            session.close()
            return models.ErrorMessage("User is not the job owner"), 403

        job_apps = (
            session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        applicant_ids = [application.id for application in job_apps]
        update_ids = [int(application["application_id"]) for application in body]

        if not set(update_ids).issubset(set(applicant_ids)):
            session.close()
            return models.ErrorMessage("Invalid ID provided"), 400

        if not all([applicant["status"] in VALID_STATUSES for applicant in body]):
            session.close()
            return models.ErrorMessage("Invalid status provided"), 400

        try:
            orm_models = []
            for application in body:
                app_orm = (
                    session.query(JobApplication)
                    .where(JobApplication.id == int(application["application_id"]))
                    .one()
                )
                app_orm.status = application["status"]
                orm_models.append(app_orm)

            session.add_all(orm_models)
            session.commit()
            job_apps = [model.to_dict() for model in orm_models]
            session.close()
            return job_apps, 200

        except Exception as e:
            session.close()
            print(e)
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400
