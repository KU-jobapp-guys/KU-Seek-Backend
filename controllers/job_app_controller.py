"""Module containing endpoints for job applications."""

import os
from typing import Dict
from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config, Csv
from sqlalchemy.orm import joinedload
from .job_controller import JobController
from swagger_server.openapi_server import models
from werkzeug.utils import secure_filename
from .models.job_model import Job, JobApplication
from .models.user_model import Student, Company, User
from .models.file_model import File
from .models.email_model import MailQueue, MailParameter
from .management.email.email_sender import EmailSender, GmailEmailStrategy
from .models.profile_model import Profile
from .serialization import camelize, decamelize

ALLOWED_FILE_FORMATS = config(
    "ALLOWED_FILE_FORMATS", cast=Csv(), default="application/pdf, application/msword"
)
BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")
VALID_STATUSES = ["accepted", "rejected"]
COMPANY_DASHBOARD_URL = config(
    "COMPANY_DASHBOARD_URL", default="http://localhost:5173/company/dashboard"
)
STUDENT_DASHBOARD_URL = config(
    "STUDENT_DASHBOARD_URL", default="http://localhost:5173/student/dashboard"
)


class JobApplicationController:
    """Controller for handling job application operations."""

    def __init__(self, database):
        """Init the class."""
        self.db = database

    @role_required(["Student"])
    def create_job_application(self, job_id: int):
        """Create a new job application from the request body."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        form = decamelize(request.form)
        files = decamelize(request.files)

        session = self.db.get_session()

        job: Job = session.query(Job).where(Job.id == job_id).one_or_none()
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

        saved_files = []

        try:
            # Process application letter
            letter = files.get("application_letter")
            if not letter:
                session.close()
                return models.ErrorMessage(
                    "Missing required application letter file"
                ), 400

            if letter.content_type not in ALLOWED_FILE_FORMATS:
                session.close()
                return models.ErrorMessage("Invalid letter file type provided"), 400

            # Create letter file record
            letter_file_name = secure_filename(letter.filename)
            letter_file_extension = os.path.splitext(letter_file_name)[1]

            letter_model = File(
                owner=UUID(token_info["uid"]),
                file_name=letter_file_name,
                file_path="temp",
                file_type="letter",
            )
            session.add(letter_model)
            session.flush()  # Get the ID

            # Save letter file with ID
            letter_file_path = (
                f"{BASE_FILE_PATH}/{letter_model.id}{letter_file_extension}"
            )
            letter_full_path = os.path.join(os.getcwd(), letter_file_path)
            letter_model.file_path = letter_file_path

            letter.save(letter_full_path)
            saved_files.append(letter_full_path)

            # Check if resume is an existing file ID
            resume = form.get("resume")
            if resume:
                # Resume is an existing file ID, just link it
                job_application.resume = int(resume)
                job_application.letter_of_application = letter_model.id

                session.add(job_application)
                session.commit()

                job_app_data = job_application.to_dict()
                job_app_data = camelize(job_app_data)
                session.close()

                return job_app_data, 200

            # Process new resume file
            resume = files.get("resume")
            if not resume:
                session.close()
                # Cleanup letter file
                if os.path.exists(letter_full_path):
                    os.remove(letter_full_path)
                return models.ErrorMessage("Missing required resume file"), 400

            if resume.content_type not in ALLOWED_FILE_FORMATS:
                session.close()
                # Cleanup letter file
                if os.path.exists(letter_full_path):
                    os.remove(letter_full_path)
                return models.ErrorMessage("Invalid resume file type provided"), 400

            # Create resume file record
            resume_file_name = secure_filename(resume.filename)
            resume_file_extension = os.path.splitext(resume_file_name)[1]

            resume_model = File(
                owner=UUID(token_info["uid"]),
                file_name=resume_file_name,
                file_path="temp",
                file_type="resume",
            )
            session.add(resume_model)
            session.flush()  # Get the ID

            # Save resume file with ID
            resume_file_path = (
                f"{BASE_FILE_PATH}/{resume_model.id}{resume_file_extension}"
            )
            resume_full_path = os.path.join(os.getcwd(), resume_file_path)
            resume_model.file_path = resume_file_path

            resume.save(resume_full_path)
            saved_files.append(resume_full_path)

            # Update job application with file IDs
            job_application.resume = resume_model.id
            job_application.letter_of_application = letter_model.id

            session.add(job_application)
            session.commit()

            job_app_data = job_application.to_dict()

            # queue mail to be sent to the company
            company = session.query(Company).where(Company.id == job.company_id).one()
            company_user = session.query(User).where(User.id == company.user_id).one()
            current_mail = (
                session.query(MailQueue)
                .where(
                    MailQueue.recipient == company_user.email,
                    MailQueue.topic == f"New applicants for {job.title}",
                )
                .one_or_none()
            )
            if current_mail:
                applicant_count = int(current_mail.get_param("ApplicantCount"))
                applicant_count += 1
                current_mail.set_param("ApplicantCount", str(applicant_count))
                session.commit()
                session.close()

                return job_app_data, 200

            mail = MailQueue(
                recipient=company_user.email,
                topic=f"New applicants for {job.title}",
                template="new_applicants",
                parameters=[
                    MailParameter(key="ApplicantCount", value="1"),
                    MailParameter(key="JobTitle", value=f"{job.title}"),
                    MailParameter(key="CompanyName", value=f"{company.company_name}"),
                    MailParameter(
                        key="DashboardLink", value=f"{COMPANY_DASHBOARD_URL}"
                    ),
                ],
            )
            session.add(mail)
            session.commit()
            job_app_data = camelize(job_app_data)
            session.close()

            return job_app_data, 200

        except Exception:
            # Rollback database transaction
            session.rollback()
            session.close()

            # Cleanup saved files on error
            for file_path in saved_files:
                if os.path.exists(file_path):
                    os.remove(file_path)

            return models.ErrorMessage("Failed to create job application"), 404

    @role_required(["Student"])
    def fetch_user_job_applications(self):
        """Fetch all job applications belonging to the owner."""
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        session = self.db.get_session()

        profile = (
            session.query(Profile)
            .where(Profile.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

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

        job_controller = JobController(self.db)

        formatted_apps = []
        for j_app in job_apps:
            mapped_job = None
            try:
                mapped_job = job_controller._JobController__job_with_company_terms_tags(
                    session, [j_app.job], single_response=True
                )
            except Exception:
                mapped_job = {
                    "jobId": str(j_app.job.id) if j_app.job else None,
                    "company": None,
                    "role": j_app.job.title if j_app.job else None,
                }
            app_obj = {
                "id": j_app.id,
                "applicant": {
                    "user_id": str(j_app.student_id),
                    "first_name": j_app.first_name,
                    "last_name": j_app.last_name,
                    "contact_email": j_app.contact_email,
                    "location": (profile.location if profile else None),
                },
                "job": mapped_job,
                "resume": j_app.resume,
                "letter_of_application": j_app.letter_of_application,
                "years_of_experience": j_app.years_of_experience,
                "expected_salary": j_app.expected_salary,
                "phone_number": j_app.phone_number,
                "status": j_app.status,
                "applied_at": j_app.applied_at,
            }

            formatted_apps.append(app_obj)

        session.close()

        formatted_apps = [camelize(a) for a in formatted_apps]

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

        formatted_apps = []
        for j_app in job_apps:
            applicant_profile = (
                session.query(Profile)
                .join(Student, Profile.user_id == Student.user_id)
                .filter(Student.id == j_app.student_id)
                .one_or_none()
            )

            formatted_apps.append(
                {
                    "id": j_app.id,
                    "applicant": {
                        "user_id": str(j_app.student_id),
                        "first_name": j_app.first_name,
                        "last_name": j_app.last_name,
                        "contact_email": j_app.contact_email,
                        "location": (
                            applicant_profile.location if applicant_profile else None
                        ),
                    },
                    "resume": j_app.resume,
                    "letter_of_application": j_app.letter_of_application,
                    "years_of_experience": j_app.years_of_experience,
                    "expected_salary": j_app.expected_salary,
                    "phone_number": j_app.phone_number,
                    "status": j_app.status,
                    "applied_at": j_app.applied_at,
                }
            )

        session.close()

        # convert to camelCase keys for frontend
        formatted_apps = [camelize(a) for a in formatted_apps]

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
                    {applicationId: str, status: str}

        returns A copy of a list of updated job applications
        """
        user_token = request.headers.get("access_token")
        token_info = decode(jwt=user_token, key=SECRET_KEY, algorithms=["HS512"])

        if not body:
            return models.ErrorMessage("No job applications provided"), 400

        body = decamelize(body)

        session = self.db.get_session()

        company = (
            session.query(Company)
            .where(Company.user_id == UUID(token_info["uid"]))
            .one_or_none()
        )

        if not company:
            session.close()
            return models.ErrorMessage("Company not found"), 400

        company_name = company.company_name
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

        if not all([applicant.status == "pending" for applicant in job_apps]):
            session.close()
            return models.ErrorMessage("Invalid job application ID provided"), 400

        applicant_ids = [application.id for application in job_apps]
        update_ids = [int(application["application_id"]) for application in body]

        if not set(update_ids).issubset(set(applicant_ids)):
            session.close()
            return models.ErrorMessage("Invalid job application ID provided"), 400

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

            # handle emails

            for application in job_apps:
                if application["status"] == "accepted":
                    mail_file = "application_accepted"
                    subject = "Application Accepted"
                else:
                    mail_file = "application_rejected"
                    subject = "Application Rejected"
                try:
                    email = EmailSender(GmailEmailStrategy())
                    email.send_email(
                        application["contact_email"],
                        subject,
                        mail_file,
                        template_args=[
                            ("JobTitle", f"{job.title}"),
                            ("CompanyName", f"{company_name}"),
                            ("ApplicationLink", f"{STUDENT_DASHBOARD_URL}"),
                        ],
                    )
                except Exception:
                    # logger here
                    pass

            # convert to camelCase keys for frontend
            job_apps = [camelize(a) for a in job_apps]

            return job_apps, 200

        except Exception as e:
            session.close()
            print(e)
            return models.ErrorMessage(f"Database exception occurred: {e}"), 400
