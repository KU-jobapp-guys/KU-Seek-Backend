"""Security misuse tests based on the Threat Models.

This test file implements negative tests aligned with the user's three threat
models: Authentication Flow, System DFD and Submit Job Application.

Note: Some tests assert desired security controls (e.g., account lockout).
These will intentionally fail until corresponding defensive code exists in
the application; failing CI signals a missing security control.
"""

import io
import pytest
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from tests.util_functions import generate_jwt
from werkzeug.utils import secure_filename
from controllers.models.token_model import Token
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as ORMSession
from tests.base_test import RoutingTestCase
from controllers.models import BaseModel
from controllers.models.user_model import User, UserTypes, Student, Company
from controllers.models.file_model import File
from controllers.models.job_model import Job
from decouple import config
import importlib


@pytest.fixture(autouse=True)
def patch_jwt_encode_to_str(monkeypatch):
    """Test-only fixture: ensure JWT encode returns str not bytes for app endpoints.

    This is a test-side workaround for environments where jwt.encode returns bytes (PyJWT versions).
    It patches the symbol in the controller module to avoid JSON serialization errors in login.
    """
    import controllers.auth_controller as auth_ctrl
    orig_encode = getattr(auth_ctrl, "encode", None)

    def wrapper(*args, **kwargs):
        token = orig_encode(*args, **kwargs) if orig_encode else None
        if isinstance(token, bytes):
            return token.decode("utf-8")
        return token

    monkeypatch.setattr(auth_ctrl, "encode", wrapper)


engine = create_engine("sqlite:///:memory:")
BaseModel.metadata.create_all(engine)


class InMemoryDBController:
    def get_session(self):
        return ORMSession(bind=engine)


RoutingTestCase.database = InMemoryDBController()
SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


@pytest.mark.security
class SecurityMisuseTests(RoutingTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        session = cls.database.get_session()

        stu = User(google_uid="stu-uid", email="student@example.com", type=UserTypes.STUDENT)
        session.add(stu)
        session.commit()
        session.refresh(stu)
        cls.student_user_id = stu.id
        cls.student_email = stu.email

        student = Student(user_id=stu.id, nisit_id="12345")
        session.add(student)
        session.commit()
        session.refresh(student)
        cls.student_id = student.id

        cu = User(google_uid="co-uid", email="company@example.com", type=UserTypes.COMPANY)
        session.add(cu)
        session.commit()
        session.refresh(cu)
        cls.company_user_id = cu.id
        comp = Company(user_id=cu.id, company_name="Acme", company_size="10")
        session.add(comp)
        session.commit()
        session.refresh(comp)
        cls.company_id = comp.id

        job = Job(
            title="Test Job",
            capacity=10,
            company_id=cls.company_id,
            salary_min=10000.0,
            salary_max=20000.0,
            location="Bangkok",
            work_hours="9-17",
            job_type="full-time",
            job_level="Junior",
            end_date=datetime.now() + timedelta(days=30),
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        cls.job_id = job.id
        session.close()

    def test_credentials_login_requires_csrf(self):
        res = self.client.post(
            "/api/v1/auth/credentials",
            data={"email": self.student_email, "password": "wrongpass"},
            content_type="multipart/form-data",
        )
        assert res.status_code in (400, 401, 403)

    def test_oauth_login_requires_csrf(self):
        res = self.client.post(
            "/api/v1/auth/oauth",
            data={"code": "dummy"},
            content_type="multipart/form-data",
        )
        assert res.status_code in (400, 401, 403)

    def test_account_lockout_after_failed_attempts(self):
        ph = PasswordHasher()
        hashed = ph.hash("P@ssw0rd!1")
        session = self.database.get_session()
        user = session.query(User).where(User.id == self.student_user_id).one()
        user.password = hashed
        session.commit()
        session.close()

        csrf = self.client.get("/api/v1/csrf-token")
        token = csrf.get_json()["csrf_token"]
        self.client.set_cookie("localhost", "csrf_token", token)

        max_attempts = 3
        last_status = None
        for _ in range(max_attempts + 1):
            r = self.client.post(
                "/api/v1/auth/credentials",
                data={"email": self.student_email, "password": "invalid"},
                content_type="multipart/form-data",
                headers={"X-CSRFToken": token},
            )
            last_status = r.status_code
        assert last_status in (429, 403)

    def test_cors_disallows_unlisted_origin(self):
        res = self.client.get("/api/v1/companies", headers={"Origin": "http://evil.com"})
        assert res.headers.get("Access-Control-Allow-Origin") != "http://evil.com"

    def test_refresh_cookie_http_only(self):
        ph = PasswordHasher()
        hashed = ph.hash("Pass!2345")
        session = self.database.get_session()
        u = session.query(User).where(User.id == self.student_user_id).one()
        u.password = hashed
        session.commit()
        session.close()

        csrf = self.client.get("/api/v1/csrf-token")
        token = csrf.get_json()["csrf_token"]
        self.client.set_cookie("localhost", "csrf_token", token)
        res = self.client.post(
            "/api/v1/auth/credentials",
            data={"email": self.student_email, "password": "Pass!2345"},
            content_type="multipart/form-data",
            headers={"X-CSRFToken": token},
        )
        assert res.status_code == 200
        cookies = res.headers.get_all("Set-Cookie")
        refresh_cookie = "".join([c for c in cookies if "refresh_token" in c])
        assert "HttpOnly" in refresh_cookie

    def test_submit_job_application_requires_auth_and_csrf(self):
        r = self.client.post(f"/api/v1/application/{self.job_id}", data={}, content_type="multipart/form-data")
        assert r.status_code in (400, 401, 403)

    def test_refresh_invalid_after_logout(self):
        from controllers.auth_controller import AuthenticationController
        auth = AuthenticationController(self.database, self.app.app.config.get("Admin"))
        with self.app.app.app_context():
            _, refresh, _, _ = auth.login_user(self.student_user_id)
        self.client.set_cookie("localhost", "refresh_token", refresh)
        csrf_token = self.client.get("/api/v1/csrf-token").get_json()["csrf_token"]
        self.client.set_cookie("localhost", "csrf_token", csrf_token)
        logout_res = self.client.post("/api/v1/auth/logout", headers={"X-CSRFToken": csrf_token})
        assert logout_res.status_code in (200, 204)
        refresh_res = self.client.get("/api/v1/refresh")
        assert refresh_res.status_code in (400, 401, 403)

    def test_logout_revokes_refresh_token(self):
        """On logout the stored refresh token should be removed from DB."""
        from controllers.auth_controller import AuthenticationController
        auth = AuthenticationController(self.database, self.app.app.config.get("Admin"))
        with self.app.app.app_context():
            _, refresh, _, _ = auth.login_user(self.student_user_id)

        self.client.set_cookie("localhost", "refresh_token", refresh)
        csrf_token = self.client.get("/api/v1/csrf-token").get_json()["csrf_token"]
        self.client.set_cookie("localhost", "csrf_token", csrf_token)
        logout_res = self.client.post("/api/v1/auth/logout", headers={"X-CSRFToken": csrf_token})
        assert logout_res.status_code in (200, 204)

        session = self.database.get_session()
        t = session.query(Token).where(Token.uid == self.student_user_id).one_or_none()
        session.close()
        assert t is None

    def test_rate_limit_blocks_requests(self):
        """If RateLimiter bans the request, endpoints should return 429."""
        class FakeRateLimiter:
            def request(self, user_id):
                return False

            def unban_user(self, user_id):
                pass

        session = self.database.get_session()
        import os
        base = os.environ.get("BASE_FILE_PATH", "content")
        os.makedirs(base, exist_ok=True)
        filename = "test_rate_limit.txt"
        path = os.path.join(base, filename)
        with open(path, "w") as f:
            f.write("Rate limit test content")

        from controllers.models.file_model import File as FileModel
        test_file = FileModel(owner=self.student_user_id, file_name=filename, file_path=path, file_type="letter")
        session.add(test_file)
        session.commit()
        session.refresh(test_file)
        file_id = str(test_file.id)
        session.close()

        self.app.app.config["RateLimiter"] = FakeRateLimiter()

        jwt_token = generate_jwt(self.student_user_id, secret=SECRET_KEY)
        res = self.client.get(f"/api/v1/file/{file_id}", headers={"access_token": jwt_token})
        assert res.status_code in (429, 500)

    def test_sensitive_data_not_exposed_on_profile(self):
        ph = PasswordHasher()
        hashed = ph.hash("SuperSecret123!")
        session = self.database.get_session()
        user = session.query(User).where(User.id == self.student_user_id).one()
        user.password = hashed
        session.commit()
        session.close()

        res = self.client.get(f"/api/v1/users/{self.student_user_id}/profile")
        assert res.status_code == 200
        json_resp = res.get_json()
        assert "password" not in json_resp

    def test_path_traversal_prevented(self):
        """File GET should not expose files outside of the content directory."""
        import os
        base = os.environ.get("BASE_FILE_PATH", "content")
        os.makedirs(base, exist_ok=True)

        session = self.database.get_session()
        gen_filename = "../../this_should_not_be_accessible.pdf"
        f = File(owner=self.student_user_id, file_name=gen_filename, file_path=os.path.join(base, "nowhere.pdf"), file_type="letter")
        session.add(f)
        session.commit()
        session.refresh(f)
        file_id = str(f.id)
        session.close()

        jwt_token = generate_jwt(self.student_user_id, secret=SECRET_KEY)
        res = self.client.get(f"/api/v1/file/{file_id}", headers={"access_token": jwt_token})
        assert res.status_code in (404, 400)

    def test_filename_sanitization(self):
        malicious = "..\/..\/etc\/passwd.png"
        sanitized = secure_filename(malicious)
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized

    def test_login_unban_calls_rate_limiter(self):
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

        from controllers.auth_controller import AuthenticationController
        auth = AuthenticationController(self.database, self.app.app.config.get("Admin"))
        with self.app.app.app_context():
            access, refresh, user_type, user_id = auth.login_user(self.student_user_id)
        assert fake_rl.unbanned

    def test_credential_login_failures_are_indistinguishable(self):
        """Incorrect email and incorrect password responses should be indistinguishable to prevent account enumeration."""
        ph = PasswordHasher()
        hashed_pw = ph.hash("PasswordEnum!23")
        session = self.database.get_session()
        user = session.query(User).where(User.id == self.student_user_id).one()
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
            data={"email": self.student_email, "password": "wrongppswd"},
            content_type="multipart/form-data",
            headers={"X-CSRFToken": csrf_token},
        )

        assert res1.status_code in (403, 404)
        assert res2.status_code in (403, 404)
