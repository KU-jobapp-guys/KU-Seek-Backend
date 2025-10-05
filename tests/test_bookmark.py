from decouple import config
from base_test import RoutingTestCase
from controllers.models import Bookmark
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
        res = self.client.get(f"/api/v1/bookmarks?user_id={self.student_user1_id}")
        self.assertTrue(isinstance(res.get_json(), list))
        self.assertEqual(res.status_code, 200)

    def test_post_new_bookmarked(self):
        """Test add new bookmarked job."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.post(
            "/api/v1/bookmarks",
            headers={
                "X-CSRFToken": csrf_token,
                "access_token": jwt
            },
            json={
                "job_id": 1
            }
        )

        data = res.json

        self.assertEqual(res.status_code, 201)
        self.assertEqual(1, data["job_id"])
        self.assertEqual(1, data["student_id"])
