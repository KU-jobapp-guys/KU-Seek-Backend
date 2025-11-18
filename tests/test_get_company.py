"""Tests for company endpoints."""

from decouple import config
from base_test import RoutingTestCase
from util_functions import add_mockup_data, generate_jwt

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class CompanyTestCase(RoutingTestCase):
    """Test company endpoints."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

    def test_get_authenticated_company(self):
        """GET /company returns the authenticated user's company."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)

        res = self.client.get("/api/v1/company", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        expected_keys = {
            "userId",
            "companyId",
            "companyName",
            "jobCount",
            "profilePhoto",
            "bannerPhoto",
            "industry",
            "location",
        }

        for k in expected_keys:
            self.assertIn(k, data, f"Missing field in company response: {k}")

        self.assertEqual(data["userId"], str(self.user1_id))

    def test_get_all_companies(self):
        """GET /companies returns a list of companies with expected shape."""
        res = self.client.get("/api/v1/companies")
        self.assertEqual(res.status_code, 200)

        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)

        company = data[0]
        expected_keys = {
            "userId",
            "companyId",
            "companyName",
            "jobCount",
            "profilePhoto",
            "bannerPhoto",
            "industry",
            "location",
        }

        for k in expected_keys:
            self.assertIn(k, company, f"Missing field in company response: {k}")

    def test_get_company_unauthorized(self):
        """GET /company without token returns 401 Unauthorized."""
        res = self.client.get("/api/v1/company")
        self.assertEqual(res.status_code, 401)

    def test_get_company_not_found(self):
        """GET /company for a user without a company returns 404."""
        jwt = generate_jwt(self.professor_user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/company", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 404)
