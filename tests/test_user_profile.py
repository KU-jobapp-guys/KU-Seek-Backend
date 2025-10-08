"""Module for testing the Profile features."""

from base_test import RoutingTestCase
from util_functions import add_mockup_data


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

    def test_get_profile_correct_response_type(self):
        """Test fetching a profile returns correct JSON object."""
        res = self.client.get(f"/api/v1/users/{self.user1_id}/profile")
        self.assertTrue(isinstance(res.get_json(), dict))
        