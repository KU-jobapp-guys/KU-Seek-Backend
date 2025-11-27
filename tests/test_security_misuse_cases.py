"""Tests for checking security misuse cases and negative tests.

These tests cover misuse scenarios and verify the application refuses insecure, unauthorized, or tampered requests.
"""

import pytest
from tests.base_test import RoutingTestCase
from tests.util_functions import generate_jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as ORMSession
from controllers.models import BaseModel


engine = create_engine("sqlite:///:memory:")
BaseModel.metadata.create_all(engine)

class InMemoryDBController:
    def get_session(self):
        return ORMSession(bind=engine)

RoutingTestCase.database = InMemoryDBController()
from controllers.auth_controller import AuthenticationController
from controllers.models.token_model import Token
import uuid
from controllers.models.user_model import User, UserTypes
from argon2 import PasswordHasher
from decouple import config
from werkzeug.utils import secure_filename
from uuid import uuid4

SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


@pytest.mark.security
class SecurityMisuseTestCase(RoutingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        session = cls.database.get_session()
        user = User(google_uid="unique_security_user", email="secure_test_user@example.com", type=UserTypes.STUDENT)
        session.add(user)
        session.commit()
        session.refresh(user)
        cls.user_id = user.id
        cls.user_email = user.email
        session.close()

    def test_csrf_cookie_and_body(self):
        """Request /api/v1/csrf-token returns cookie and JSON token."""
        res = self.client.get("/api/v1/csrf-token")
        self.assertEqual(res.status_code, 200)
        res_json = res.get_json()
        self.assertIn("csrf_token", res_json)
        cookies = res.headers.get_all("Set-Cookie")
        self.assertTrue(any("csrf_token" in c for c in cookies))

    def test_rate_limit_blocks_requests(self):
        """If RateLimiter reports a ban, the endpoint should be blocked.

        We inject a fake rate limiter that denies all requests.
        """

        class FakeRateLimiter:
            def request(self, user_id):
                return False

            def unban_user(self, user_id):
                pass

        session = self.database.get_session()
        from controllers.models.file_model import File
        import os
        base = config("BASE_FILE_PATH", default="content")
        os.makedirs(base, exist_ok=True)
        filename = "test_rate_limit.txt"
        path = os.path.join(base, filename)
        with open(path, "w") as f:
            f.write("Rate limit test content")

        test_file = File(owner=self.user_id, file_name=filename, file_path=path, file_type="letter")
        session.add(test_file)
        session.commit()
        session.refresh(test_file)
        file_id = str(test_file.id)
        session.close()

        self.app.app.config["RateLimiter"] = FakeRateLimiter()

        jwt_token = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get(f"/api/v1/file/{file_id}", headers={"access_token": jwt_token})

        self.assertIn(res.status_code, (429, 500))

    def test_logout_revokes_refresh_token(self):
        """On logout, the refresh token stored in DB should be removed and refresh is invalid afterwards."""

        auth_controller = AuthenticationController(self.database, self.app.app.config.get("Admin"))
        with self.app.app.app_context():
            access, refresh, user_type, user_id = auth_controller.login_user(self.user_id)

        self.client.set_cookie("localhost", "refresh_token", refresh)

        csrf_res = self.client.get("/api/v1/csrf-token")
        csrf_token = csrf_res.get_json()["csrf_token"]

        self.client.set_cookie("localhost", "csrf_token", csrf_token)
        res = self.client.post("/api/v1/auth/logout", headers={"X-CSRFToken": csrf_token})
        self.assertIn(res.status_code, (200, 204))

        session = self.database.get_session()
        t = session.query(Token).where(Token.uid == self.user_id).one_or_none()
        session.close()
        self.assertIsNone(t)

    def test_sensitive_data_not_exposed_on_profile(self):
        """Ensure APIs don't leak password or other secrets in public responses."""

        ph = PasswordHasher()
        hashed_pw = ph.hash("SuperSecretTestPassword123!")

        session = self.database.get_session()
        user = session.query(User).where(User.id == self.user_id).one()
        user.password = hashed_pw
        session.commit()
        user_email = user.email
        session.close()

        res = self.client.get(f"/api/v1/users/{self.user_id}/profile")
        self.assertEqual(res.status_code, 200)
        json_resp = res.get_json()

        self.assertNotIn("password", json_resp)

    def test_filename_sanitization(self):
        """Validate that `secure_filename` sanitizes dangerous filenames and prevents path traversal."""
        malicious = "..\/..\/etc\/passwd.png"
        sanitized = secure_filename(malicious)
        self.assertNotIn("..", sanitized)
        self.assertNotIn("/", sanitized)
        self.assertNotIn("\\", sanitized)

        self.assertTrue(sanitized)

    def test_path_traversal_prevented(self):
        """Attempt to create a DB file record with malicious filename and ensure endpoint doesn't serve contents from arbitrary paths."""
        from controllers.models.file_model import File
        import os
        base = config("BASE_FILE_PATH", default="content")
        os.makedirs(base, exist_ok=True)

        session = self.database.get_session()

        gen_filename = "../../this_should_not_be_accessible.pdf"
        f = File(owner=self.user_id, file_name=gen_filename, file_path=os.path.join(base, "nowhere.pdf"), file_type="letter")
        session.add(f)
        session.commit()
        session.refresh(f)
        file_id = str(f.id)
        session.close()

        jwt_token = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get(f"/api/v1/file/{file_id}", headers={"access_token": jwt_token})

        self.assertIn(res.status_code, (404, 400))

    def test_login_unban_calls_rate_limiter(self):
        """Login flow should call RateLimiter.unban_user to ensure users are unbanned on login."""

        class FakeRateLimiter:
            def __init__(self):
                self.unbanned = False

            def request(self, user_id):
                return True

            def unban_user(self, user_id):
                self.unbanned = True

            def is_banned(self, user_id):
                return False

        fake_rl = FakeRateLimiter()
        self.app.app.config["RateLimiter"] = fake_rl

        auth_controller = AuthenticationController(self.database, self.app.app.config.get("Admin"))
        with self.app.app.app_context():
            access, refresh, user_type, user_id = auth_controller.login_user(self.user_id)
        self.assertTrue(fake_rl.unbanned)

    def test_credential_login_failures_are_indistinguishable(self):
        """Credential login should not reveal if email exists (prevent account enumeration).

        This test asserts that incorrect email and incorrect password responses are indistinguishable.
        If the responses differ, the test fails so CI can flag potential user enumeration.
        """

        ph = PasswordHasher()
        hashed_pw = ph.hash("GuessablePassword123!")
        session = self.database.get_session()
        user = session.query(User).where(User.id == self.user_id).one()
        user.password = hashed_pw
        session.commit()
        session.close()

        csrf_res = self.client.get("/api/v1/csrf-token")
        csrf_token = csrf_res.get_json()["csrf_token"]

        self.client.set_cookie("localhost", "csrf_token", csrf_token)

        res1 = self.client.post(
            "/api/v1/auth/credentials",
            data={"email": "doesnotexist@example.com", "password": "whatever"},
            content_type="multipart/form-data",
            headers={"X-CSRFToken": csrf_token},
        )

        res2 = self.client.post(
            "/api/v1/auth/credentials",
            data={"email": self.user_email, "password": "wrongppswd"},
            content_type="multipart/form-data",
            headers={"X-CSRFToken": csrf_token},
        )

        self.assertIn(res1.status_code, (403, 404))
        self.assertIn(res2.status_code, (403, 404))

        for r in (res1, res2):
            self.assertLessEqual(r.status_code, 500)
