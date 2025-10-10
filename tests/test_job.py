"""Module for testing the Job features."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class JobTestCase(RoutingTestCase):
    """Test case for job."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

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
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={
                "capacity": 2,
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
                "work_hours": "9:00 AM - 5:00 PM",
            },
        )

        self.assertEqual(res.status_code, 201)

    def test_job_post_response_data(self):
        """Test the data that send back to the frontend is the correct data."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        job_payload = {
            "capacity": 4,
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
            "work_hours": "6:00 AM - 8:00 PM",
        }

        jwt = generate_jwt(self.user2_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=job_payload,
        )

        self.assertEqual(res.status_code, 201)

        data = res.json
        self.assertEqual(data["title"], job_payload["title"])
        self.assertEqual(data["company_id"], 2)
        self.assertEqual(data["salary_min"], job_payload["salary_min"])
        self.assertEqual(data["salary_max"], job_payload["salary_max"])

    def test_job_post_missing_required_fields(self):
        """Test posting a job without required fields should fail."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        # Missing 'title' and 'salary_min'
        invalid_payload = {
            "capacity": 2,
            "description": "This should fail due to missing fields.",
            "end_date": "2025-12-31T23:59:59Z",
            "job_level": "Senior-level",
            "job_type": "full-time",
            "location": "Bangkok, Thailand",
            "salary_max": 120000,
            "work_hours": "9:00 AM - 5:00 PM",
        }

        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=invalid_payload,
        )

        self.assertEqual(res.status_code, 400)

    def test_filter_job__status_code(self):
        """Test the status code of filter Job API."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        filter_list = {
            "capacity": 1,
            "title": "Ghost Job",
            "end_date": "2025-12-31T23:59:59Z",
            "job_level": "Entry-level",
            "job_type": "full-time",
            "location": "Nowhere",
            "salary_min": 10000,
            "salary_max": 20000,
            "work_hours": "9:00 AM - 5:00 PM",
        }

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json=filter_list,
        )

        self.assertEqual(res.status_code, 200)

        # weird field name
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"who_tao?": True},
        )

        self.assertEqual(res.status_code, 400)

    def test_filter_job_invalid_value(self):
        """Test filtering jobs with invalid data types should return 400."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        # Test invalid salary_min (not a number)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"salary_min": "not_a_number"},
        )
        self.assertEqual(res.status_code, 400)

        # Test invalid capacity (not an integer)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"capacity": "three"},
        )
        self.assertEqual(res.status_code, 400)

        # Test invalid end_date format
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"end_date": "invalid-date"},
        )
        self.assertEqual(res.status_code, 400)

        # Test invalid skill_names (not an array)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"skill_names": "should_be_array"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("skill_names must be an array", res.json["message"])

        # Test invalid tag_names (not an array)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"tag_names": "should_be_array"},
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("tag_names must be an array", res.json["message"])

    def test_filter_job_returns_correct_filtered_data(self):
        """Test that filtered jobs return the correct matching data."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        # Filter by title - should return job with "Senior Python Developer"
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"title": "Senior Python"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        self.assertIn("Senior Python", data[0]["title"])

        # Filter by location - should return job in "Bangkok"
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"location": "Bangkok"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertIn("Bangkok", job["location"])

        # Filter by salary range - should return jobs with salary_min >= 80000
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"salary_min": 80000},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertGreaterEqual(job["salary_min"], 80000)

        # Filter by job_level - should return jobs with "Junior-level"
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"job_level": "Junior-level"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertEqual(job["job_level"], "Junior-level")

        # Filter by company_name - should return jobs from "TechCorp"
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"company_name": "TechCorp"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertIn("TechCorp", job["company"]["company_name"])

    def test_filter_by_multiple_cliteria(self):
        """Test the Job filter api by have multiple value in the body."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"job_type": "full-time", "location": "Bangkok"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertEqual(job["job_type"], "full-time")
            self.assertIn("Bangkok", job["location"])

    def test_filter_with_no_match_data(self):
        """Test filter API by give non exist job title to the body."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"title": "NonExistentJobTitle12345"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(len(data), 0)

    def test_filter_with_empty_body_returns_all_jobs(self):
        """Test that filtering with empty body {} returns all jobs."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json

        self.assertEqual(len(data), 2)

        # Verify it returns the same jobs as GET /api/v1/jobs
        all_jobs_res = self.client.get("/api/v1/jobs")
        all_jobs_data = all_jobs_res.json

        self.assertEqual(len(data), len(all_jobs_data))

        self.assertEqual(data, all_jobs_data)
