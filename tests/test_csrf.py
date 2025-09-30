"""Module for testing authentication and authorization."""

from base_test import RoutingTestCase
from util_functions import generate_jwt
from datetime import datetime, timedelta
from decouple import config
from uuid import uuid4
from controllers.models import User


class AuthenticationTestCase(RoutingTestCase):
    """Test case for authentication."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_no_csrf_token(self):
        """Test fetching a POST API with no csrf token."""
        res = self.client.post("/api/v1/test/tasks", json={"name": "some task"})
        self.assertEqual(res.status_code, 400)

    def test_invalid_csrf_token(self):
        """Test fetching a POST API with an invalid csrf token."""
        res = self.client.post(
            "/api/v1/test/tasks",
            headers={"X-CSRFToken": "legit-token"},
            json={"name": "some task"},
        )
        self.assertEqual(res.status_code, 400)

    def test_csrf_token(self):
        """Test fetching a POST API with a valid csrf token."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        res = self.client.post(
            "/api/v1/test/tasks",
            headers={"X-CSRFToken": csrf_token},
            json={"name": "some task"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, {"name": "some task", "completed": False, "id": 1})
