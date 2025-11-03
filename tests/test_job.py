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
        self.assertTrue(len(res.get_json()), 1)

    def test_get_specific_job(self):
        """
        Test fetching a Job GET API.

        It should return specific job data.
        """
        res = self.client.get("/api/v1/jobs?job_id=1")
        data = res.json

        self.assertEqual(data["jobId"], "1")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.get_json()), 1)
        self.assertEqual(data["jobId"], "1")

    def test_output_all_field(self):
        """Test that the data have all field base on schema."""
        res = self.client.get("/api/v1/jobs")

        data = res.json

        job = data[0]
        expected_fields = {
            "company",
            "contacts",
            "description",
            "jobId",
            "jobLevel",
            "jobType",
            "location",
            "pendingApplicants",
            "postTime",
            "role",
            "salaryMax",
            "salaryMin",
            "skills",
            "status",
            "totalApplicants",
        }

        for field in expected_fields:
            self.assertIn(field, job, f"Missing field: {field}")

        self.assertIsInstance(job["company"], str)

        if job.get("contacts"):
            contact = job["contacts"][0]
            for field in ("type", "link"):
                self.assertIn(field, contact, f"Missing contact field: {field}")

        if job.get("skills"):
            skill = job["skills"][0]
            self.assertIsInstance(skill, str)

        if job.get("tags"):
            tag = job["tags"][0]
            self.assertIsInstance(tag, str)

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
                "endDate": "2025-12-31T23:59:59Z",
                "jobLevel": "Senior-level",
                "jobType": "full-time",
                "location": "Bangkok, Thailand",
                "salaryMax": 120000,
                "salaryMin": 80000,
                "skillNames": ["Python", "Django", "SQL"],
                "tagNames": ["Remote", "Backend"],
                "title": "Senior Python Developer",
                "workHours": "9:00 AM - 5:00 PM",
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
            "endDate": "2026-08-06T23:59:59Z",
            "jobLevel": "Junior-level",
            "jobType": "full-time",
            "location": "Osaka, Japan",
            "salaryMax": 20000,
            "salaryMin": 15000,
            "skillNames": ["Django"],
            "tagNames": ["Backend", "Fullstack"],
            "title": "Junior Slave Developer",
            "workHours": "6:00 AM - 8:00 PM",
        }

        jwt = generate_jwt(self.user2_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=job_payload,
        )

        self.assertEqual(res.status_code, 201)

        data = res.json
        self.assertEqual(data["role"], job_payload["title"])
        self.assertIsInstance(data["company"], str)
        self.assertEqual(data["salaryMin"], job_payload["salaryMin"])
        self.assertEqual(data["salaryMax"], job_payload["salaryMax"])

    def test_job_post_missing_required_fields(self):
        """Test posting a job without required fields should fail."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        # Missing 'title' and 'salary_min'
        invalid_payload = {
            "capacity": 2,
            "description": "This should fail due to missing fields.",
            "endDate": "2025-12-31T23:59:59Z",
            "jobLevel": "Senior-level",
            "jobType": "full-time",
            "location": "Bangkok, Thailand",
            "salaryMax": 120000,
            "workHours": "9:00 AM - 5:00 PM",
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
            "endDate": "2025-12-31T23:59:59Z",
            "jobLevel": "Entry-level",
            "jobType": "full-time",
            "location": "Nowhere",
            "salaryMin": 10000,
            "salaryMax": 20000,
            "workHours": "9:00 AM - 5:00 PM",
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
            json={"salaryMin": "not_a_number"},
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
            json={"endDate": "invalid-date"},
        )
        self.assertEqual(res.status_code, 400)

        # Test invalid skill_names (not an array)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"skillNames": "should_be_array"},
        )
        self.assertEqual(res.status_code, 400)
        jb = res.json or {}
        if "message" in jb:
            self.assertIn("skill_names must be an array", jb["message"])
        else:
            self.assertIn("is not of type 'array'", str(jb.get("detail", "")))

        # Test invalid tag_names (not an array)
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"tagNames": "should_be_array"},
        )
        self.assertEqual(res.status_code, 400)
        jb = res.json or {}
        if "message" in jb:
            self.assertIn("tag_names must be an array", jb["message"])
        else:
            self.assertIn("is not of type 'array'", str(jb.get("detail", "")))

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
        self.assertIn("Senior Python", data[0]["role"])

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
            json={"salaryMin": 80000},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertGreaterEqual(job["salaryMin"], 80000)

        # Filter by job_level - should return jobs with "Junior-level"
        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"jobLevel": "Junior-level"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertEqual(job["jobLevel"], "Junior-level")

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"companyName": "TechCorp"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)

    def test_filter_by_multiple_cliteria(self):
        """Test the Job filter api by have multiple value in the body."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token},
            json={"jobType": "full-time", "location": "Bangkok"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)
        for job in data:
            self.assertEqual(job["jobType"], "full-time")
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

        self.assertEqual(len(data), 3)

        all_jobs_res = self.client.get("/api/v1/jobs")
        all_jobs_data = all_jobs_res.json

        self.assertEqual(len(data), len(all_jobs_data))

        self.assertEqual(data, all_jobs_data)

    def test_filter_is_owner_returns_only_own_jobs(self):
        """Return only jobs posted by the authenticated company.

        This verifies that when the request body contains "is_owner": true the
        API filters jobs to those owned by the JWT's company.
        """
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        jwt = generate_jwt(self.user2_id, secret=SECRET_KEY)

        job_payload = {
            "capacity": 1,
            "description": "Owner job test.",
            "endDate": "2026-01-01T23:59:59Z",
            "jobLevel": "Mid-level",
            "jobType": "full-time",
            "location": "Bangkok, Thailand",
            "salaryMax": 50000,
            "salaryMin": 30000,
            "skillNames": ["React"],
            "tagNames": ["OwnerTest"],
            "title": "Owner Job",
            "workHours": "9:00 AM - 5:00 PM",
        }

        post_res = self.client.post(
            "/api/v1/jobs",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=job_payload,
        )

        self.assertEqual(post_res.status_code, 201)
        posted_job = post_res.json

        res = self.client.post(
            "/api/v1/jobs/search",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"isOwner": True},
        )

        print("SKY", res.json)

        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertGreater(len(data), 0)

        for job in data:
            self.assertEqual(job.get("company"), posted_job.get("company"))

        job_ids = [j.get("jobId") for j in data]
        self.assertIn(posted_job.get("jobId"), job_ids)
