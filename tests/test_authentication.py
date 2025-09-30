"""Module for testing authentication and authorization."""

from base_test import RoutingTestCase
from util_functions import generate_jwt
from datetime import datetime, timedelta
from decouple import config
from uuid import uuid4
from controllers.models import User


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class AuthenticationTestCase(RoutingTestCase):
    """Test case for authentication."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        # create a user in the database
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Student")
        session.add(user)
        session.commit()
        user = session.query(User).first()
        cls.user_id = user.id
        session.close()


    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_no_authentication(self):
        """Test fetching a protected API with no authenticaion."""
        res = self.client.get("/api/v1/test/tasks")
        self.assertEqual(res.status_code, 401)

    def test_invalid_jwt_secret(self):
        """Test fetching a protected API with invalid JWT signature."""
        jwt = generate_jwt(uuid4())
        res = self.client.get("/api/v1/test/tasks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 403)
        self.assertIn("Invalid authentication token", res.json["message"])

    def test_expired_authentication(self):
        """Test fetching a protected API with an expired JWT."""
        issued_at = int((datetime.now() - timedelta(hours=1)).timestamp())
        jwt = generate_jwt(uuid4(), exp=issued_at, secret=SECRET_KEY)
        res = self.client.get("/api/v1/test/tasks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 403)
        self.assertIn("Token is expired", res.json["message"])

    def test_authentication(self):
        """Test fetching a protected API with valid credentials."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/test/tasks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        self.assertEqual([], res.json)


class AuthorizationTestCase(RoutingTestCase):
    """Test case for authorization."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        # create 2 users in the database
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Student")
        session.add(user)
        session.commit()
        user = session.query(User).where(User.google_uid == "12345").one()
        cls.user1_id = user.id

        user = User(google_uid="98765", email="h@kc3r@gmail.com", type="Staff")
        session.add(user)
        session.commit()
        user = session.query(User).where(User.google_uid == "98765").one()
        cls.user2_id = user.id
        session.close()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_invalid_authorization(self):
        """Test fetching a protected API with non-privilaged authorization."""
        jwt = generate_jwt(self.user2_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/test/tasks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 403)
        self.assertIn("User does not have authorization", res.json["message"])


    def test_authorization(self):
        """Test fetching a protected API with valid credentials."""
        jwt = generate_jwt(self.user1_id, secret=SECRET_KEY)
        res = self.client.get("/api/v1/test/tasks", headers={"access_token": jwt})
        self.assertEqual(res.status_code, 200)
        self.assertEqual([], res.json)
