"""Module for testing the Professor Connection features."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ProfessorConnectionTestCase(RoutingTestCase):
    """Test case for professor connections."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_get_empty_connections(self):
        """Test that it returns an empty list for professor with no connections."""
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertTrue(isinstance(res.get_json(), list))
        self.assertEqual(res.status_code, 200)

    def test_get_connections_status_code(self):
        """Test fetching connections returns 200 status code."""
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/connections",
            headers={"access_token": jwt},
        )
        self.assertEqual(res.status_code, 200)

    def test_post_new_connection_status_code(self):
        """Test creating a new connection returns 201 status code."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        
        connection_payload = {
            "company_id": 1,
        }
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)

    def test_post_new_connection_returns_correct_data(self):
        """Test that created connection returns the correct data."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user2_id, secret=SECRET_KEY)
        
        connection_payload = {
            "company_id": 2,
        }
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(res.status_code, 201)
        data = res.json
        self.assertEqual(data["company_id"], connection_payload["company_id"])
        self.assertIn("id", data)
        self.assertIn("professor_id", data)
        self.assertIn("created_at", data)

    def test_post_connection_empty_body(self):
        """Test creating a connection with empty body returns 400."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        
        res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={},
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("company_id' is a required property", res.json["detail"])
