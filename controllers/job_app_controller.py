"""Module containing endpoints for job applications."""

import os
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
from .models.user_model import Student, Company
from .models.file_model import File
from .models.profile_model import Profile

ALLOWED_FILE_FORMATS = config(
    "ALLOWED_FILE_FORMATS", cast=Csv(), default="application/pdf, application/msword"
)
BASE_FILE_PATH = config("BASE_FILE_PATH", default="content")
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

        # commit transaction with rollback on error
        try:
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

        except Exception as e:
            # rollback database transaction
            session.rollback()
            session.close()

            # cleanup saved files on error
            if os.path.exists(resume_file_path):
                os.remove(resume_file_path)
            if os.path.exists(letter_file_path):
                os.remove(letter_file_path)

            return models.ErrorMessage("Failed to create job application: ", e), 404

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

        return formatted_apps, 200

    @role_required(["Company"])
    def fetch_job_application_from_job_post(self, job_id):
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
                models.JobApplication(
                    id=j_app.id,
                    applicant={
                        "user_id": str(j_app.student_id),
                        "first_name": j_app.first_name,
                        "last_name": j_app.last_name,
                        "contact_email": j_app.contact_email,
                        "location": (
                            applicant_profile.location if applicant_profile else None
                        ),
                    },
                    resume=j_app.resume,
                    letter_of_application=j_app.letter_of_application,
                    years_of_experience=j_app.years_of_experience,
                    expected_salary=j_app.expected_salary,
                    phone_number=j_app.phone_number,
                    status=j_app.status,
                    applied_at=j_app.applied_at,
                )
            )

        session.close()

        return formatted_apps, 200
