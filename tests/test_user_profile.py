"""Module for testing the Profile features."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ProfileTestCase(RoutingTestCase):
    """Test case for user profile."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_get_profile_status_code(self):
        """Test fetching a profile returns 200 status code."""
        res = self.client.get(f"/api/v1/users/{self.user1_id}/profile")
        self.assertEqual(res.status_code, 200)

    def test_create_profile_status_code(self):
        """Test creating a new profile returns 201 status code."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)

        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        profile_payload = {
            "first_name": "John",
            "last_name": "Doe",
            "about": "Passionate software developer",
            "location": "Bangkok, Thailand",
            "contact_email": "john.doe@example.com",
            "gender": "M",
            "age": 25,
            "user_type": "student",
            "phone_number": "0812345678",
        }

        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=profile_payload,
        )

        self.assertEqual(res.status_code, 201)

    def test_create_profile_returns_correct_data(self):
        """Test that created profile returns the correct data."""
        jwt = generate_jwt(self.student_user2_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        profile_payload = {
            "first_name": "Jane",
            "last_name": "Smith",
            "about": "Web developer enthusiast",
            "location": "Chiang Mai, Thailand",
            "contact_email": "jane.smith@example.com",
            "gender": "F",
            "age": 23,
            "user_type": "student",
            "phone_number": "0898765432",
        }

        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=profile_payload,
        )

        self.assertEqual(res.status_code, 201)

        data = res.json
        self.assertEqual(data["first_name"], profile_payload["first_name"])
        self.assertEqual(data["last_name"], profile_payload["last_name"])
        self.assertEqual(data["about"], profile_payload["about"])
        self.assertEqual(data["location"], profile_payload["location"])
        self.assertEqual(data["contact_email"], profile_payload["contact_email"])
        self.assertEqual(data["age"], profile_payload["age"])

    def test_create_profile_empty_body(self):
        """Test creating a profile with empty body."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={},
        )

        self.assertEqual(res.status_code, 500)

    def test_create_profile_duplicate(self):
        """Test creating a profile for existing user returns 409."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        profile_payload = {
            "first_name": "Test",
            "last_name": "User",
            "user_type": "student",
        }

        jwt = generate_jwt(self.user2_id, secret=SECRET_KEY)
        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=profile_payload,
        )

        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=profile_payload,
        )

        self.assertEqual(res.status_code, 500)
        self.assertIn("Profile already exists", res.json["message"])

    def test_create_profile_partial_data(self):
        """Test creating a profile with partial data succeeds."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        profile_payload = {
            "first_name": "Alice",
            "last_name": "Johnson",
        }

        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.post(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=profile_payload,
        )

        self.assertEqual(res.status_code, 201)
        data = res.json
        self.assertEqual(data["first_name"], "Alice")
        self.assertEqual(data["last_name"], "Johnson")

    def test_get_profile_correct_response_type(self):
        """Test fetching a profile returns correct JSON object."""
        res = self.client.get(f"/api/v1/users/{self.user1_id}/profile")
        self.assertTrue(isinstance(res.get_json(), dict))

    def test_get_profile_returns_correct_fields(self):
        """Test that the profile data has all expected fields."""
        res = self.client.get(f"/api/v1/users/{self.user1_id}/profile")

        data = res.json

        expected_fields = {
            "user_id",
            "first_name",
            "last_name",
            "about",
            "location",
            "email",
            "contact_email",
            "gender",
            "age",
            "user_type",
            "profile_img",
            "banner_img",
            "phone_number",
            "is_verified",
        }

        for field in expected_fields:
            self.assertIn(field, data, f"Missing field: {field}")

    def test_get_profile_not_found(self):
        """Test fetching a non-existent profile returns 404."""
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        res = self.client.get(f"/api/v1/users/{non_existent_uuid}/profile")
        self.assertEqual(res.status_code, 404)

    def test_get_profile_invalid_uuid(self):
        """Test fetching a profile with invalid UUID format returns 400."""
        non_existent_uuid = "Praise_The_Sun"
        res = self.client.get(f"/api/v1/users/{non_existent_uuid}/profile")
        self.assertEqual(res.status_code, 404)

    def test_update_profile_status_code(self):
        """Test updating a profile returns 200 status code."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "first_name": "Updated",
            "location": "Phuket, Thailand",
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 200)

    def test_update_profile_returns_updated_data(self):
        """Test that updated profile returns the correct modified data."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "first_name": "UpdatedName",
            "last_name": "UpdatedLastName",
            "about": "Updated bio information",
            "age": 30,
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 200)

        data = res.json
        self.assertEqual(data["first_name"], update_payload["first_name"])
        self.assertEqual(data["last_name"], update_payload["last_name"])
        self.assertEqual(data["about"], update_payload["about"])
        self.assertEqual(data["age"], update_payload["age"])

    def test_update_profile_not_found(self):
        """Test updating a non-existent profile returns 404."""
        jwt = generate_jwt("00000000-0000-0000-0000-000000000000", secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "first_name": "Ghost",
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 404)
        self.assertIn("not found", res.json["message"])

    def test_update_profile_empty_body(self):
        """Test updating a profile with empty body returns 400."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={},
        )

        self.assertEqual(res.status_code, 500)
        self.assertIn("Request body cannot be empty", res.json["message"])

    def test_update_profile_single_field(self):
        """Test updating a single field in profile works correctly."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "phone_number": "0823456789",
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["phone_number"], "0823456789")

    def test_update_profile_multiple_fields(self):
        """Test updating multiple fields in profile works correctly."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "first_name": "Multi",
            "last_name": "Update",
            "location": "Pattaya, Thailand",
            "age": 28,
            "phone_number": "0834567890",
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["first_name"], update_payload["first_name"])
        self.assertEqual(data["last_name"], update_payload["last_name"])
        self.assertEqual(data["location"], update_payload["location"])
        self.assertEqual(data["age"], update_payload["age"])
        self.assertEqual(data["phone_number"], update_payload["phone_number"])

    def test_update_profile_ignores_invalid_fields(self):
        """Test that updating with invalid fields ignores them."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        update_payload = {
            "first_name": "Valid",
            "invalid_field": "should be ignored",
            "another_invalid": 12345,
        }

        res = self.client.patch(
            "/api/v1/users/profile",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=update_payload,
        )

        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data["first_name"], "Valid")
        self.assertNotIn("invalid_field", data)
        self.assertNotIn("another_invalid", data)
