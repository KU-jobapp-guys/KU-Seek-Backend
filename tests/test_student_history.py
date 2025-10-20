"""Module for testing the Student history endpoints."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt
from datetime import datetime

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class StudentHistoryTestCase(RoutingTestCase):
    """Test case for student view histories."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def _csrf_and_jwt(self, user_id):
        jwt = generate_jwt(user_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        return jwt, csrf_token

    def test_get_histories_empty(self):
        """GET /student/histories should return an empty list when none exist."""
        jwt, _ = self._csrf_and_jwt(self.student_user1_id)
        res = self.client.get(
            "/api/v1/student/histories",
            headers={"access_token": jwt},
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.get_json(), list))
        self.assertEqual(len(res.get_json()), 0)

    def test_post_creates_history_and_gets_it(self):
        """POST should create a history entry and GET should return it."""
        jwt, csrf = self._csrf_and_jwt(self.student_user1_id)

        payload = {"job_id": 1}
        post_res = self.client.post(
            "/api/v1/student/histories",
            headers={"X-CSRFToken": csrf, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(post_res.status_code, 200)
        data = post_res.get_json()
        self.assertIn("job_id", data)
        self.assertIn("student_id", data)
        self.assertIn("viewed_at", data)

        get_res = self.client.get(
            "/api/v1/student/histories",
            headers={"access_token": jwt},
        )
        self.assertEqual(get_res.status_code, 200)
        arr = get_res.get_json()
        self.assertTrue(len(arr) >= 1)
        found = [h for h in arr if h.get("job_id") == 1]
        self.assertTrue(len(found) >= 1)

    def test_post_updates_existing_timestamp(self):
        """Posting same job_id twice should update the viewed_at timestamp."""
        jwt, csrf = self._csrf_and_jwt(self.student_user1_id)

        payload = {"job_id": 2}
        first = self.client.post(
            "/api/v1/student/histories",
            headers={"X-CSRFToken": csrf, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(first.status_code, 200)
        first_data = first.get_json()
        first_ts = first_data.get("viewed_at")
        self.assertIsNotNone(first_ts)

        second = self.client.post(
            "/api/v1/student/histories",
            headers={"X-CSRFToken": csrf, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(second.status_code, 200)
        second_data = second.get_json()
        second_ts = second_data.get("viewed_at")
        self.assertIsNotNone(second_ts)

        fdt = datetime.fromisoformat(first_ts.replace("Z", ""))
        sdt = datetime.fromisoformat(second_ts.replace("Z", ""))
        self.assertGreaterEqual(sdt, fdt)

    def test_trim_keeps_only_latest_15(self):
        """Creating more than 15 histories should trim the oldest ones."""
        jwt, csrf = self._csrf_and_jwt(self.student_user1_id)

        # create 17 distinct job histories
        for jid in range(100, 117):
            res = self.client.post(
                "/api/v1/student/histories",
                headers={"X-CSRFToken": csrf, "access_token": jwt},
                json={"job_id": jid},
            )
            self.assertEqual(res.status_code, 200)

        # Now GET and ensure only 15 remain and oldest two (100,101) are gone
        get_res = self.client.get(
            "/api/v1/student/histories",
            headers={"access_token": jwt},
        )
        self.assertEqual(get_res.status_code, 200)
        arr = get_res.get_json()
        self.assertEqual(len(arr), 15)
        job_ids = {h["job_id"] for h in arr}
        self.assertNotIn(100, job_ids)
        self.assertNotIn(101, job_ids)
