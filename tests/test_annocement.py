"""Tests for professor announcements endpoints."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt
from controllers.models import Profile

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class AnnouncementTestCase(RoutingTestCase):
    """Test case for announcements endpoints."""

    @classmethod
    def setUpClass(cls):
        """Create users, professors and companies needed for announcement tests."""
        super().setUpClass()
        add_mockup_data(cls)

        session = cls.database.get_session()

        session.add_all(
            [
                Profile(
                    user_id=cls.professor_user1_id,
                    first_name="ProfA",
                    last_name="One",
                    profile_img="/img/p1.png",
                    about="Professor One",
                    user_type="professor",
                ),
                Profile(
                    user_id=cls.professor_user2_id,
                    first_name="ProfB",
                    last_name="Two",
                    profile_img="/img/p2.png",
                    about="Professor Two",
                    user_type="professor",
                ),
                Profile(
                    user_id=cls.user1_id,
                    first_name=None,
                    last_name=None,
                    about="Company One",
                    user_type="company",
                ),
                Profile(
                    user_id=cls.user2_id,
                    first_name=None,
                    last_name=None,
                    about="Company Two",
                    user_type="company",
                ),
            ]
        )
        session.commit()
        session.close()

    @classmethod
    def tearDownClass(cls):
        """Clean up database after tests complete."""
        super().tearDownClass()

    def test_get_annoucements(self):
        """GET /api/v1/annoucements should return a list of announcements.

        This test ensures the endpoint responds with 200 and each announcement
        contains id, title, content, created_at and professor_* fields.
        """
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get(
            "/api/v1/annoucements",
            headers={"access_token": jwt},
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)

        if data:
            ann = data[0]
            expected = {
                "id",
                "professor",
                "professorPosition",
                "department",
                "company",
                "companyIndustry",
                "tags",
            }
            for field in expected:
                self.assertIn(field, ann)

    def test_post_connection_creates_annoucement(self):
        """Posting a new connection should create an announcement."""
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)

        connection_payload = {"company_id": 2}

        post_res = self.client.post(
            "/api/v1/connections",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=connection_payload,
        )

        self.assertEqual(post_res.status_code, 201)
        conn_data = post_res.get_json()
        self.assertIn("id", conn_data)

        get_res = self.client.get(
            "/api/v1/annoucements",
            headers={"access_token": jwt},
        )
        self.assertEqual(get_res.status_code, 200)
        anns = get_res.get_json()
        self.assertIsInstance(anns, list)

        found = [a for a in anns if a.get("id") == conn_data.get("id")]
        self.assertTrue(found, "No announcement found for the created connection")

        ann = found[0]
        self.assertIn("professor", ann)
        self.assertIn("company", ann)
        self.assertIn("tags", ann)
