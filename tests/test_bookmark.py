"""Module for testing the Bookmark features."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class BookmarkTestCase(RoutingTestCase):
    """Test case for bookmarking the job."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_get_empty_bookmarked(self):
        """Test that it return []."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/bookmarks"
            ,headers={"access_token": jwt},
        )
        self.assertTrue(isinstance(res.get_json(), list))
        self.assertEqual(res.status_code, 200)

    def test_post_new_bookmarked(self):
        """Test add new bookmarked job."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.post(
            "/api/v1/bookmarks",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"job_id": 1},
        )

        data = res.json

        self.assertEqual(res.status_code, 201)
        self.assertEqual(1, data["job_id"])
        self.assertEqual(1, data["student_id"])

    def test_post_then_delete_bookmarked(self):
        """Test creating a bookmark and then deleting it."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.student_user2_id, secret=SECRET_KEY)

        res = self.client.post(
            "/api/v1/bookmarks",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"job_id": 1},
        )

        self.assertEqual(res.status_code, 201)
        created_data = res.json
        self.assertEqual(1, created_data["job_id"])

        res = self.client.delete(
            "/api/v1/bookmarks?job_id=1",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertEqual(res.status_code, 200)
        deleted_data = res.json
        self.assertEqual(1, deleted_data["job_id"])
        self.assertEqual(2, deleted_data["student_id"])

        res = self.client.get("/api/v1/bookmarks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        bookmarks = res.json
        self.assertEqual(len(bookmarks), 0)

    def test_delete_nonexistent_bookmark(self):
        """Test deleting a bookmark that doesn't exist should return 400."""
        res = self.client.get("/api/v1/csrf-token?job")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)

        res = self.client.delete(
            "/api/v1/bookmarks?job_id=9999",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertEqual(res.status_code, 500)
        self.assertIn("Bookmark not found", res.json["message"])

    def test_delete_bookmark_invalid_field(self):
        """Test deleting with invalid field should return 400."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)

        res = self.client.delete(
            "/api/v1/bookmarks?invalid_field=123",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )

        self.assertEqual(res.status_code, 400)
