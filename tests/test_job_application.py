"""Module for testing authentication and authorization."""

import os
import shutil
from io import BytesIO
from base_test import RoutingTestCase
from util_functions import generate_jwt
from datetime import datetime, timedelta
from decouple import config
from controllers.models import User, Job, Company, Student, JobApplication, File


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class JobApplicationTestCase(RoutingTestCase):
    """Test case for all job application endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        # create a company and student in the database
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Student")
        company_user = User(
            google_uid="9876", email="greed@greedcorp.com", type="Company"
        )
        session.add_all([user, company_user])
        session.commit()
        session.refresh(user)
        session.refresh(company_user)
        company = Company(
            user_id=company_user.id,
            company_name="Acme Corporation",
            company_type="Private",
            company_industry="Technology",
            company_size="51-200",
            company_website="https://www.acme.com",
            full_location="New York, NY, USA",
        )
        student = Student(
            user_id=user.id,
            nisit_id="S12345678",
            gpa=3.75,
            interests="Programming, AI, Robotics",
        )

        session.add_all([company, student])
        session.commit()
        session.refresh(company)
        session.refresh(student)
        cls.user_id = user.id
        cls.student_id = student.id
        cls.company_id = company_user.id

        # create 3 jobs in the database
        job1 = Job(
            company_id=company.id,
            title="nice tech job",
            salary_min=0,
            salary_max=0,
            location="7 street",
            work_hours="10",
            job_type="tech",
            job_level="internship",
            status="approved",
            visibility=True,
            capacity=2,
            end_date=datetime.now() + timedelta(hours=1),
        )

        job2 = Job(
            company_id=company.id,
            title="Junior Software Developer",
            salary_min=30000,
            salary_max=45000,
            location="123 Innovation Avenue",
            work_hours="9-5",
            job_type="Software Engineering",
            job_level="Entry-level",
            status="approved",
            visibility=True,
            capacity=3,
            end_date=datetime.now() + timedelta(hours=1),
        )

        job3 = Job(
            company_id=company.id,
            title="Fake job linkedin pro max",
            salary_min=30000,
            salary_max=45000,
            location="123 Innovation Avenue",
            work_hours="9-5",
            job_type="Software Engineering",
            job_level="Entry-level",
            status="approved",
            visibility=True,
            capacity=0,
            end_date=datetime.now() + timedelta(hours=1),
        )

        session.add_all([job1, job2, job3])
        session.commit()

        job_application = JobApplication(
            job_id=job1.id,
            student_id=student.id,
            first_name="John",
            last_name="Doe",
            contact_email="faker@gmail.com",
            resume="some real file id",
            letter_of_application="some other real file id",
            years_of_experience="3",
            expected_salary="50000 < 80000",
            phone_number="0123456789",
            status="pending",
            applied_at=datetime.now(),
        )
        session.add(job_application)
        session.commit()
        session.refresh(job_application)
        cls.job_app_id = job_application.id
        session.close()

        cls.test_dir = os.path.join(os.getcwd(), "content", "test")

        # Ensure the directory exists
        os.makedirs(cls.test_dir, exist_ok=True)

        # Define file paths
        cls.resume_path = os.path.join(cls.test_dir, "resume.pdf")
        cls.letter_path = os.path.join(cls.test_dir, "letter.pdf")

        # Write dummy non-empty files
        with open(cls.resume_path, "wb") as f:
            f.write(b"%PDF-1.4\nFake resume PDF content for testing\n")

        with open(cls.letter_path, "wb") as f:
            f.write(b"%PDF-1.4\nFake letter PDF content for testing\n")

        # Safety checks
        assert os.path.exists(cls.resume_path), f"Missing file: {cls.resume_path}"
        assert os.path.exists(cls.letter_path), f"Missing file: {cls.letter_path}"
        assert os.path.getsize(cls.resume_path) > 0, "Resume file is empty"
        assert os.path.getsize(cls.letter_path) > 0, "Letter file is empty"

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        # get all files logged in the testing database and delete it
        session = cls.database.get_session()
        files = session.query(File).all()
        for file in files:
            os.remove(os.getcwd() + "/" + file.file_path)

        session.close()

        # destroy the /content/test directory along with the test files
        shutil.rmtree(cls.test_dir)
        super().tearDownClass()

    def test_invalid_role_access(self):
        """A User with an unauthorized role cannot access the Job Application APIs."""
        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/application", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 403)
        self.assertIn("User does not have auth", res.json["message"])

    def test_get_self_job_applications(self):
        """A Student can get their submited job applications."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/application", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 1)

    def test_get_job_applications_from_job_post(self):
        """A Company can get all job applications belonging to a job post."""
        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/application/1", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 1)

    def test_submit_job_application_to_full_job(self):
        """A student cannot create a job application to a job post that is full."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)

        resume = BytesIO(b"Fake resume content for testing")
        letter = BytesIO(b"Fake application letter content for testing")

        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "yearsOfExperience": "2",
            "expectedSalary": "15000",
            "phoneNumber": "0812345678",
            "resume": (resume, "resume.pdf", "application/pdf"),
            "applicationLetter": (
                letter,
                "letter.pdf",
                "application/pdf",
            ),
        }

        # POST to the API route with files + form data for job 3
        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.post(
            "/api/v1/application/3",
            data=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
            content_type="multipart/form-data",
        )

        self.assertEqual(res.status_code, 400)

    def test_submit_job_application(self):
        """A Student can create a new job application."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)

        resume = BytesIO(b"Fake resume content for testing")
        letter = BytesIO(b"Fake application letter content for testing")

        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "yearsOfExperience": "2",
            "expectedSalary": "15000",
            "phoneNumber": "0812345678",
            "resume": (resume, "resume.pdf", "application/pdf"),
            "applicationLetter": (
                letter,
                "letter.pdf",
                "application/pdf",
            ),
        }

        # POST to the API route with files + form data for job 2
        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.post(
            "/api/v1/application/2",
            data=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
            content_type="multipart/form-data",
        )

        # validate response
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn("firstName", json_data)
        self.assertEqual(json_data["firstName"], "John")

        res = self.client.get("/api/v1/application", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 2)

    def test_same_job_application_submission(self):
        """A Student cannot apply for a job twice."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)

        # POST to the API route with files + form data for job 2
        csrf = self.client.get("/api/v1/csrf-token")

        resume = BytesIO(b"Fake resume content for testing2")
        letter = BytesIO(b"Fake application letter content for testing2")

        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "yearsOfExperience": "2",
            "expectedSalary": "15000",
            "phoneNumber": "0812345678",
            "resume": (resume, "resume2.pdf", "application/pdf"),
            "applicationLetter": (
                letter,
                "letter2.pdf",
                "application/pdf",
            ),
        }

        # POST to the API route with files + form data for job 1
        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.post(
            "/api/v1/application/1",
            data=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
            content_type="multipart/form-data",
        )

        self.assertEqual(res.status_code, 400)

    def test_update_job_application_without_auth(self):
        """A user must authenticate to use the job application update API."""
        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            "/api/v1/application/update/1",
            json=[],
            headers={"X-CSRFToken": csrf.json["csrf_token"]},
        )
        self.assertEqual(res.status_code, 401)

    def test_update_job_application_with_invalid_role(self):
        """Only company users can update job applicant status."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)

        data = [{"applicationId": self.job_app_id, "status": "accepted"}]

        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            "/api/v1/application/update/1",
            json=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("User does not have auth", res.json["message"])

    def test_update_job_application_for_unowned_job(self):
        """A company may only update applications for jobs they own."""
        # Create another company, job and job application
        session = self.database.get_session()
        try:
            other_company_user = User(
                google_uid="5555", email="other@company.com", type="Company"
            )
            session.add(other_company_user)
            session.commit()
            session.refresh(other_company_user)

            other_company = Company(
                user_id=other_company_user.id,
                company_name="Other Corp",
                company_type="Private",
                company_industry="Finance",
                company_size="11-50",
                company_website="https://www.other.com",
                full_location="Bangkok, Thailand",
            )
            session.add(other_company)
            session.commit()
            session.refresh(other_company)

            other_job = Job(
                company_id=other_company.id,
                title="Different Job",
                salary_min=0,
                salary_max=0,
                location="Other street",
                work_hours="8",
                job_type="finance",
                job_level="internship",
                status="approved",
                visibility=True,
                capacity=2,
                end_date=datetime.now() + timedelta(hours=1),
            )
            session.add(other_job)
            session.commit()
            session.refresh(other_job)
            other_job_id = other_job.id

            job_application = JobApplication(
                job_id=other_job_id,
                student_id=self.student_id,
                first_name="John",
                last_name="Doe",
                contact_email="faker@gmail.com",
                resume="some real file id",
                letter_of_application="some other real file id",
                years_of_experience="3",
                expected_salary="50000 < 80000",
                phone_number="0123456789",
                status="pending",
                applied_at=datetime.now(),
            )
            session.add(job_application)
            session.commit()
            session.refresh(job_application)
            job_application_id = job_application.id
        finally:
            session.close()

        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)

        data = [{"applicationId": job_application_id, "status": "accepted"}]

        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            f"/api/v1/application/update/{other_job_id}",
            json=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
        )
        self.assertEqual(res.status_code, 403)
        self.assertIn("User is not the job owner", res.json["message"])

    def test_update_job_application_for_invalid_application(self):
        """Only valid job applications can be updated."""
        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)

        # Use a non-existent application ID
        data = [{"applicationId": 99999999999, "status": "accepted"}]

        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            "/api/v1/application/update/1",
            json=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid job application ID provided", res.json["message"])

    def test_update_one_job_application(self):
        """A company can update a job application."""
        # Get the existing application ID from job 1

        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)

        data = [{"applicationId": self.job_app_id, "status": "accepted"}]

        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            "/api/v1/application/update/1",
            json=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 1)

        # Verify the status was updated in the database
        session = self.database.get_session()
        try:
            updated_app = (
                session.query(JobApplication)
                .where(JobApplication.id == self.job_app_id)
                .one()
            )
            self.assertEqual(updated_app.status, "accepted")
        finally:
            session.close()

    def test_update_multiple_job_applications(self):
        """A company can update multiple job applications at once."""
        # Create additional applications for job 2
        session = self.database.get_session()

        # Create a second student
        user2 = User(google_uid="11111", email="student2@gmail.com", type="Student")
        session.add(user2)
        session.commit()
        session.refresh(user2)

        student2 = Student(
            user_id=user2.id,
            nisit_id="S87654321",
            gpa=3.50,
            interests="Data Science, ML",
        )
        session.add(student2)
        session.commit()
        session.refresh(student2)

        # Create second application
        job_application2 = JobApplication(
            job_id=2,
            student_id=student2.id,
            first_name="Jane",
            last_name="Smith",
            contact_email="jane@gmail.com",
            resume="file_id_2",
            letter_of_application="file_id_3",
            years_of_experience="1",
            expected_salary="40000",
            phone_number="0987654321",
            status="pending",
            applied_at=datetime.now(),
        )
        session.add(job_application2)
        session.commit()

        # Get both application IDs
        job_apps = session.query(JobApplication).where(JobApplication.job_id == 2).all()
        app_ids = [app.id for app in job_apps]
        session.close()

        jwt = generate_jwt(self.company_id, secret=SECRET_KEY)

        data = [
            {"applicationId": app_ids[0], "status": "accepted"},
            {"applicationId": app_ids[1], "status": "rejected"},
        ]

        csrf = self.client.get("/api/v1/csrf-token")
        res = self.client.patch(
            "/api/v1/application/update/2",
            json=data,
            headers={"access_token": jwt, "X-CSRFToken": csrf.json["csrf_token"]},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json), 2)

        # Verify both statuses were updated
        session = self.database.get_session()
        try:
            app1 = (
                session.query(JobApplication)
                .where(JobApplication.id == app_ids[0])
                .one()
            )
            app2 = (
                session.query(JobApplication)
                .where(JobApplication.id == app_ids[1])
                .one()
            )
            self.assertEqual(app1.status, "accepted")
            self.assertEqual(app2.status, "rejected")
        finally:
            session.close()
