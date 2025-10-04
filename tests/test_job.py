"""Module for testing authentication and authorization."""

from base_test import RoutingTestCase
from util_functions import generate_jwt
from datetime import datetime, timedelta
from decouple import config
from uuid import uuid4
from controllers.models import User, Company, Tags, Terms, Job


class JobTestCase(RoutingTestCase):
    """Test case for authentication."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        # create 2 users in the database
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Company")
        session.add(user)
        session.commit()
        user = session.query(User).where(User.google_uid == "12345").one()
        cls.user1_id = user.id

        user = User(google_uid="98765", email="h@kc3r@gmail.com", type="Company")
        session.add(user)
        session.commit()
        user = session.query(User).where(User.google_uid == "98765").one()
        cls.user2_id = user.id

        # Add temporary company data for testing
        company = Company(
            user_id=cls.user1_id,
            company_name="TechCorp Ltd.",
            company_type="Private",
            company_industry="Software",
            company_size="200-500",
            company_website="https://www.techcorp.com",
            full_location="Bangkok, Thailand"
        )

        company_2 = Company(
            user_id=cls.user2_id,
            company_name="For the Darksouls",
            company_type="Private",
            company_industry="Bodyguard",
            company_size="20-45",
            company_website="https://www.protect-you.com",
            full_location="Chiangmai, Thailand"
        )
        
        session.add(company)
        session.add(company_2)
        session.commit()

        # add tag mock data
        tag_mock_data = [
            'Artificial Intelligence',
            'Web Development',
            'Data Science',
            'Cybersecurity',
            'Cloud Computing',
            'Machine Learning',
            'Blockchain',
            'Mobile Apps'
        ]
        
        for tag_name in tag_mock_data:
            tag = Tags(
                name=tag_name
            )

            session.add(tag)

        session.commit()

        term_mock_data = [
            ('Internship', 'Opportunity'),
            ('Scholarship', 'Opportunity'),
            ('Full-time', 'Job'),
            ('Part-time', 'Job'),
            ('Remote', 'WorkType'),
            ('Onsite', 'WorkType'),
            ('Research', 'Activity'),
            ('Workshop', 'Activity')
        ]

        for term_data in term_mock_data:
            tag = Terms(
                name=term_data[0],
                type=term_data[1]
            )

            session.add(tag)

        session.commit()


        # mockup job data
        job1 = Job(
            capacity=2,
            company_id=1,
            description="Job 1",
            end_date="2025-12-31 23:59:59",
            job_level="Senior-level",
            job_type="full-time",
            location="Bangkok, Thailand",
            salary_max=120000,
            salary_min=80000,
            title="Senior Python Developer",
            work_hours="9:00 AM - 5:00 PM"
        )
        job2 = Job(
            capacity=4,
            company_id=2,
            description="Job 2",
            end_date="2026-08-06 23:59:59",
            job_level="Junior-level",
            job_type="full-time",
            location="Osaka, Japan",
            salary_max=20000,
            salary_min=15000,
            title="Junior Slave Developer",
            work_hours="6:00 AM - 8:00 PM"
        )
        session.add(job1)
        session.add(job2)
        session.commit()

        session.close()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_correct_response_type(self):
        """Test fetching a Job GET API."""
        res = self.client.get("/api/v1/jobs")
        self.assertTrue(isinstance(res.get_json(), list))
    
    def test_response_status(self):
        """Test that it return 200."""
        res = self.client.get("/api/v1/jobs")
        self.assertEqual(res.status_code, 200)
        
    def test_amout_of_data(self):
        """
        Test fetching a Job GET API.
        
        It should have 2 job datas.
        """
        res = self.client.get("/api/v1/jobs")
        self.assertTrue(len(res.get_json()), 2)

    def test_get_one_job_by_id(self):
        """
        Test fetching a Job GET API.
        
        It should return specific job data.
        """
        res = self.client.get("/api/v1/jobs?job_id=1")
        data = res.json

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.get_json()), 1)
        self.assertEqual(data["id"], 1)

    def test_output_all_field(self):
        """Test that the data have all field base on schema."""
        res = self.client.get("/api/v1/jobs")

        data = res.json

        job = data[0]  

        expected_fields = {
            "approved_by",
            "capacity",
            "company",
            "company_id",
            "created_at",
            "description",
            "end_date",
            "id",
            "job_level",
            "job_type",
            "location",
            "salary_max",
            "salary_min",
            "skills",
            "status",
            "tags",
            "title",
            "visibility",
            "work_hours",
        }

        for field in expected_fields:
            self.assertIn(field, job, f"Missing field: {field}")

        expected_company_fields = {
            "company_industry",
            "company_name",
            "company_size",
            "company_type",
            "company_website",
            "full_location",
            "id",
            "user_id",
        }
        for field in expected_company_fields:
            self.assertIn(field, job["company"], f"Missing company field: {field}")

        if job["skills"]:
            skill = job["skills"][0]
            for field in ("id", "name", "type"):
                self.assertIn(field, skill, f"Missing skill field: {field}")

        if job["tags"]:
            tag = job["tags"][0]
            for field in ("id", "name"):
                self.assertIn(field, tag, f"Missing tag field: {field}")


    def test_job_post_status_code(self):
        """Test posting jobs then check the status code."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token},
            json={
                "capacity": 2,
                "company_id": 1,
                "description": "We are looking for an experienced Python developer.",
                "end_date": "2025-12-31T23:59:59Z",
                "job_level": "Senior-level",
                "job_type": "full-time",
                "location": "Bangkok, Thailand",
                "salary_max": 120000,
                "salary_min": 80000,
                "skill_ids": [1, 2, 3],
                "tag_ids": [5, 6],
                "title": "Senior Python Developer",
                "work_hours": "9:00 AM - 5:00 PM"
            },

        )

        self.assertEqual(res.status_code, 201)

    def test_response_data(self):
        """Test the data that send back to the frontend is the correct data."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        job_payload = {
            "capacity": 4,
            "company_id": 2,
            "description": "We are looking for someone please help us.",
            "end_date": "2026-08-06T23:59:59Z",
            "job_level": "Junior-level",
            "job_type": "full-time",
            "location": "Osaka, Japan",
            "salary_max": 20000,
            "salary_min": 15000,
            "skill_ids": [2],
            "tag_ids": [2, 4],
            "title": "Junior Slave Developer",
            "work_hours": "6:00 AM - 8:00 PM"
        }

        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token},
            json=job_payload,

        )

        self.assertEqual(res.status_code, 201)

        data = res.json
        self.assertEqual(data["title"], job_payload["title"])
        self.assertEqual(data["company_id"], job_payload["company_id"])
        self.assertEqual(data["salary_min"], job_payload["salary_min"])
        self.assertEqual(data["salary_max"], job_payload["salary_max"])
    



