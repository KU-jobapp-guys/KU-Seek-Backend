"""Module for testing the Education endpoints."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class EducationTestCase(RoutingTestCase):
    """Test case for education CRUD endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_get_educations_list(self):
        """GET /educations should return a list (may be empty)."""
        res = self.client.get("/api/v1/educations")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(res.get_json(), list))

    def test_post_education_status_code(self):
        """POST /educations should return 201 on success."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        payload = {
            "curriculum_name": "Computer Science",
            "university": "Kasetsart University",
            "major": "Computer Science",
            "year_of_study": "2020-08-01",
            "graduate_year": "2024-05-15",
        }

        post_res = self.client.post(
            "/api/v1/educations",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=payload,
        )

        self.assertEqual(post_res.status_code, 201)

    def test_post_education_response_data(self):
        """POST should create and return the created education object."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        payload = {
            "curriculum_name": "Computer Science",
            "university": "Kasetsart University",
            "major": "Computer Science",
            "year_of_study": "2020-08-01",
            "graduate_year": "2024-05-15",
        }

        post_res = self.client.post(
            "/api/v1/educations",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(post_res.status_code, 201)
        data = post_res.get_json()
        for key in payload:
            self.assertIn(key, data)

        created_id = data.get("id")
        self.assertIsNotNone(created_id)
        del_res = self.client.delete(
            f"/api/v1/educations/{created_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )
        self.assertEqual(del_res.status_code, 200)

    def test_patch_education_updates(self):
        """PATCH should update a single field on an education record."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        payload = {
            "curriculum_name": "Computer Science",
            "university": "Kasetsart University",
            "major": "Computer Science",
            "year_of_study": "2020-08-01",
            "graduate_year": "2024-05-15",
        }
        post_res = self.client.post(
            "/api/v1/educations",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(post_res.status_code, 201)
        created = post_res.get_json()
        created_id = created.get("id")
        self.assertIsNotNone(created_id)

        # patch
        patch_res = self.client.patch(
            f"/api/v1/educations/{created_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json={"major": "Software Engineering"},
        )
        self.assertEqual(patch_res.status_code, 200)
        patched = patch_res.get_json()
        self.assertEqual(patched["major"], "Software Engineering")

        del_res = self.client.delete(
            f"/api/v1/educations/{created_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )
        self.assertEqual(del_res.status_code, 200)

    def test_delete_education(self):
        """DELETE should remove the education record and return it."""
        jwt = generate_jwt(self.student_user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/csrf-token")
        csrf_token = res.json["csrf_token"]

        payload = {
            "curriculum_name": "Computer Science",
            "university": "Kasetsart University",
            "major": "Computer Science",
            "year_of_study": "2020-08-01",
            "graduate_year": "2024-05-15",
        }
        post_res = self.client.post(
            "/api/v1/educations",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
            json=payload,
        )
        self.assertEqual(post_res.status_code, 201)
        created = post_res.get_json()
        created_id = created.get("id")

        del_res = self.client.delete(
            f"/api/v1/educations/{created_id}",
            headers={"X-CSRFToken": csrf_token, "access_token": jwt},
        )
        self.assertEqual(del_res.status_code, 200)
        del_data = del_res.get_json()
        self.assertEqual(del_data["id"], created_id)
