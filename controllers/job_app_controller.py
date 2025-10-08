"""Module containing endpoints for job applications."""

from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config, Csv
from sqlalchemy.orm import joinedload
from .models import User, Job, JobApplication, Student, Company, File
from swagger_server.openapi_server import models
from werkzeug.utils import secure_filename


ALLOWED_FILE_FORMATS = config(
    "ALLOWED_FILE_FORMATS", cast=Csv(), default="application/pdf, application/msword"
)
BASE_FILE_PATH = config("BASE_FILE_PATH", default="/content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class JobApplicationController:
    """Controller for handling job application operations."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    @role_required(["Student"])
    def create_job_application(self, body, job_id):
        """Create a new job application from the request body."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        form = request.form
        session = self.db.get_session()

        # handle fields
        student = (
            session.query(Student)
            .where(Student.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not student:
            session.close()
            return models.ErrorMessage("Student not found"), 400

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

        job_app_data = job_application.to_dict()

        # handle files
        resume = request.files.get("resume")
        letter = request.files.get("application_letter")

        if not resume or not letter:
            session.close()
            return models.ErrorMessage("Missing required files"), 400

        if letter not in ALLOWED_FILE_FORMATS:
            session.close()
            return models.ErrorMessage("Invalid file type provided"), 400
        if resume not in ALLOWED_FILE_FORMATS:
            session.close()
            return models.ErrorMessage("Invalid file type provided"), 400

        letter_file_name = secure_filename(letter.filename)
        resume_file_name = secure_filename(resume.filename)
        letter_file_path = BASE_FILE_PATH + "/" + letter_file_name
        resume_file_path = BASE_FILE_PATH + "/" + resume_file_name
        letter.save(letter_file_path)
        resume.save(resume_file_path)

        letter_model = File(
            owner=UUID(token_info["uid"]),
            file_name=letter_file_name,
            file_path=letter_file_path,
        )
        resume_model = File(
            owner=UUID(token_info["uid"]),
            file_name=resume_file_name,
            file_path=resume_file_path,
        )

        session.add_all([letter_model, resume_model])
        session.commit()

        # update job application with the file ids
        session.refresh(letter_model)
        session.refresh(resume_model)
        job_application.resume = resume_model.id
        job_application.letter_of_application = letter_model.id

        session.add(job_application)
        session.commit()
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
            .where(JobApplication.user_id == student.id)
            .all()
        )

        applications = [j_app.to_dict() for j_app in job_apps]
        detailed_apps = [j_app.job.to_dict() for j_app in applications]
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
            for j_app in detailed_apps
        ]

        session.close()

        return formatted_apps, 200

    @role_required(["Company"])
    def fetch_job_application_from_job_post(self, job_id):
        """Fetch all job applications for a specific job post."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        user = (
            session.query(User).where(User.id == UUID(token_info["uid"])).one_or_none()
        )

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

        if job.user_id != company.id:
            session.close()
            return models.ErrorMessage("User is not the job owner"), 403

        job_apps = (
            session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        applications = [j_app.to_dict() for j_app in job_apps]

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
            for j_app in applications
        ]

        session.close()

        return formatted_apps, 200
