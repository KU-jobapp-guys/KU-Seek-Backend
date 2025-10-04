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
            end_date="2025-12-31T23:59:59Z",
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
            end_date="2026-08-06T23:59:59Z",
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
    


    # def test_invalid_csrf_token(self):
    #     """Test fetching a POST API with an invalid csrf token."""
    #     res = self.client.post(
    #         "/api/v1/test/tasks",
    #         headers={"X-CSRFToken": "legit-token"},
    #         json={"name": "some task"},
    #     )
    #     self.assertEqual(res.status_code, 400)

    # def test_csrf_token(self):
    #     """Test fetching a POST API with a valid csrf token."""
    #     res = self.client.get("/api/v1/csrf-token")
    #     csrf_token = res.json["csrf_token"]
    #     res = self.client.post(
    #         "/api/v1/test/tasks",
    #         headers={"X-CSRFToken": csrf_token},
    #         json={"name": "some task"},
    #     )
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(res.json, {"name": "some task", "completed": False, "id": 1})
