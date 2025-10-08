"""Module containing simple testcase for app setup and tear down."""

import unittest
from controllers.db_controller import BaseController
from sqlalchemy import create_engine, text
from controllers.models import BaseModel
from app import create_app
from decouple import config


class TestingController(BaseController):
    """Controller that controlls the test database."""

    def __init__(self):
        """Instantiate from parent class and redifine the database engine."""
        super().__init__()

    def _get_testing_database(self):
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
                print("Testing database initialization successful...")

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
            self.pool = db_engine
            BaseModel.metadata.create_all(db_engine)
        except Exception as e:
            raise ConnectionRefusedError("Could not create testing database,", e)

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

    database = TestingController()

    @classmethod
    def setUpClass(cls):
        """Create an instance of the app and database."""
        cls.database._get_testing_database()

    @classmethod
    def tearDownClass(cls):
        """Destroy the testing database and close the unittest."""
        cls.database._destroy_testing_database()


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

        cls.app = create_app(cls.database)
        cls.client = cls.app.app.test_client()
