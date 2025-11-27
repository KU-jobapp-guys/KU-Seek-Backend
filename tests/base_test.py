"""Module containing simple testcase for app setup and tear down."""

import unittest
from controllers.db_controller import AbstractDatabaseController
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from controllers.models import BaseModel
import sys
import types

# If tests are running in an environment without the `redis` library, stub a minimal
# `redis` module so `controllers.db_rate_limit` can import with no errors. This keeps
# tests isolated and avoids requiring `redis` for unit test runs.
if "redis" not in sys.modules:
    class _RedisStub:
        def __init__(self, *a, **kw):
            pass

        def incr(self, *a, **kw):
            return 1

        def expire(self, *a, **kw):
            return None

        def sadd(self, *a, **kw):
            return None

        def srem(self, *a, **kw):
            return None

        def sismember(self, *a, **kw):
            return False

    sys.modules["redis"] = types.SimpleNamespace(Redis=_RedisStub)

from app import create_app
from decouple import config


class TestingController(AbstractDatabaseController):
    """Controller that controlls the test database."""

    def __init__(self):
        """Instantiate the class."""
        self.pool = self._get_database()

    def _get_testing_database(self):
        """Generate a fresh testing database."""
        self.pool = self._get_database()

    def _get_database(self):
        """Create a database for testing."""
        host = config("DB_HOST", default="127.0.0.1")
        port = config("DB_PORT", cast=int, default="1234")
        user = config("DB_USER", default="root")
        password = config("DB_PASSWORD", default="mysecrtpw123")

        connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}"

        db_engine = create_engine(
            connection_url,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10,
        )

        testing_db = config("TESTING_DB", default="unittestdb")
        try:
            with db_engine.connect() as pool:
                pool.execute(text(f"DROP DATABASE IF EXISTS {testing_db}"))
                pool.execute(text(f"CREATE DATABASE {testing_db}"))
                print("Testing database initialization sucessful...")

            # use the testing db
            connection_url = (
                f"mysql+pymysql://{user}:{password}@{host}:{port}/{testing_db}"
            )

            db_engine = create_engine(
                connection_url,
                pool_size=1,
                max_overflow=0,
                pool_timeout=10,
            )
            BaseModel.metadata.create_all(db_engine)
            return db_engine
        except Exception as e:
            raise ConnectionRefusedError("Could not create testing database,", e)

    def get_session(self):
        """Return a session object for ORM usage."""
        return Session(self.pool)

    def _destroy_testing_database(self):
        """Destory the created testing database."""
        try:
            with self.pool.connect() as pool:
                pool.execute(
                    text(f"DROP DATABASE {config('TESTING_DB', default='unittestdb')}")
                )
                print("\nTesting database removed sucessfuly...")
        except Exception as e:
            raise ConnectionRefusedError("Could not destroy testing database,", e)


class SimpleTestCase(unittest.TestCase):
    """Simple test case with database setup."""

    # Defer instantiation of TestingController so we don't attempt to connect
    # or create databases during module import. Tests may override this by
    # setting `database` before setUpClass runs.
    database = None

    @classmethod
    def setUpClass(cls):
        """Create an instance of the app and database."""
        if cls.database is None:
            cls.database = TestingController()
        # If the database controller exposes an explicit creation method,
        # call it. Otherwise assume it will create sessions lazily.
        if hasattr(cls.database, "_get_testing_database"):
            cls.database._get_testing_database()

    @classmethod
    def tearDownClass(cls):
        """Destroy the testing database and close the unittest."""
        if getattr(cls, "database", None) is not None and hasattr(cls.database, "_destroy_testing_database"):
            cls.database._destroy_testing_database()
            cls.database = None


class RoutingTestCase(SimpleTestCase):
    """Application level test cases."""

    @classmethod
    def setUpClass(cls):
        """Set up a test client of the application, along with the database."""
        super().setUpClass()

        # connexion deprication error, not our problem so ignoring it.
        import warnings

        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message=r"Passing a schema to Validator\.iter_errors is deprecated",
        )

        # Provide a fake rate limiter to avoid requiring a Redis backend during tests
        class FakeRateLimiter:
            def request(self, user_id):
                return True

            def unban_user(self, user_id):
                pass

            def ban_user(self, user_id):
                pass

            def is_banned(self, user_id):
                return False

        cls.app = create_app(cls.database)
        # Replace the RateLimiter with a fake one to avoid Redis dependency.
        cls.app.app.config["RateLimiter"] = FakeRateLimiter()
        cls.client = cls.app.app.test_client()
