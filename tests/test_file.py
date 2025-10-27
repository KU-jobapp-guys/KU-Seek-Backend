"""Module for testing file serving and downloading."""

import os
from uuid import uuid4
from base_test import RoutingTestCase
from controllers.models.file_model import File
from controllers.models.user_model import User
from decouple import config

from tests.util_functions import generate_jwt


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class FileServingTestCase(RoutingTestCase):
    """Test case for file serving."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()

        # Create a test user for authentication
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Student")
        session.add(user)
        session.commit()
        session.refresh(user)
        cls.user_id = user.id

        # Create a temporary test file
        cls.file_dir = config("BASE_FILE_PATH", default="content")
        os.makedirs(cls.file_dir, exist_ok=True)
        cls.test_file_name = "test_document.pdf"
        cls.test_file_path = os.path.join(cls.file_dir, cls.test_file_name)
        with open(cls.test_file_path, "w") as f:
            f.write("This is test file content")

        # Create a file record in the database
        test_file = File(
            owner=user.id,
            file_name=cls.test_file_name,
            file_path=cls.test_file_path,
            file_type="letter",
        )
        session.add(test_file)
        session.commit()
        session.refresh(test_file)
        cls.file_id = test_file.id
        session.close()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        # Clean up test file
        if os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)
        super().tearDownClass()

    def test_get_file_without_authentication(self):
        """A user cannot access the file endpoint without authentication."""
        response = self.client.get(f"/api/v1/file/{self.file_id}")
        self.assertEqual(response.status_code, 401)

    def test_get_file_success(self):
        """Test successfully serving a file for display."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get(
            f"/api/v1/file/{self.file_id}", headers={"access_token": jwt}
        )
        try:
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"This is test file content", res.data)
        finally:
            res.close()

    def test_get_file_not_in_database(self):
        """Test serving a file that doesn't exist in the database."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        non_existent_id = str(uuid4())
        res = self.client.get(
            f"/api/v1/file/{non_existent_id}", headers={"access_token": jwt}
        )
        self.assertEqual(res.status_code, 404)

    def test_get_file_not_on_disk(self):
        """Test serving a file that exists in DB but not on disk."""
        # Create a file record without actual file
        session = self.database.get_session()
        missing_file = File(
            owner=self.user_id,
            file_name="missing_file.pdf",
            file_path=os.path.join(self.file_dir, "missing_file.pdf"),
            file_type="letter",
        )
        session.add(missing_file)
        session.commit()
        session.refresh(missing_file)
        missing_file_id = missing_file.id
        session.close()

        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        response = self.client.get(
            f"/api/v1/file/{missing_file_id}", headers={"access_token": jwt}
        )
        self.assertEqual(response.status_code, 404)


class FileDownloadingTestCase(RoutingTestCase):
    """Test case for file downloading."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()

        # Create a test user for authentication
        session = cls.database.get_session()
        user = User(google_uid="12345", email="faker@gmail.com", type="Student")
        session.add(user)
        session.commit()
        session.refresh(user)
        cls.user_id = user.id

        # Create a temporary test file
        cls.file_dir = config("BASE_FILE_PATH", default="content")
        os.makedirs(cls.file_dir, exist_ok=True)
        cls.test_file_name = "test_document2.pdf"
        cls.test_file_path = os.path.join(cls.file_dir, cls.test_file_name)
        with open(cls.test_file_path, "w") as f:
            f.write("Downloadable content")

        # Create a file record in the database
        test_file = File(
            owner=user.id,
            file_name=cls.test_file_name,
            file_path=cls.test_file_path,
            file_type="letter",
        )
        session.add(test_file)
        session.commit()
        session.refresh(test_file)
        cls.file_id = test_file.id
        session.close()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        # Clean up test file
        if os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)
        super().tearDownClass()

    def test_download_file_without_authentication(self):
        """Test accessing file download endpoint without authentication."""
        res = self.client.get(f"/api/v1/file/download/{self.file_id}")
        self.assertEqual(res.status_code, 401)

    def test_download_file_success(self):
        """Test successfully downloading a file."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get(
            f"/api/v1/file/download/{self.file_id}", headers={"access_token": jwt}
        )
        try:
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Downloadable content", res.data)
            # Check that Content-Disposition header indicates attachment
            self.assertIn("attachment", res.headers.get("Content-Disposition", ""))
        finally:
            res.close()

    def test_download_file_not_in_database(self):
        """Test downloading a file that doesn't exist in the database."""
        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        non_existent_id = str(uuid4())
        res = self.client.get(
            f"/api/v1/file/download/{non_existent_id}", headers={"access_token": jwt}
        )
        self.assertEqual(res.status_code, 404)

    def test_download_file_not_on_disk(self):
        """Test downloading a file that exists in DB but not on disk."""
        # Create a file record without actual file
        session = self.database.get_session()
        missing_file = File(
            owner=self.user_id,
            file_name="missing_download2.txt",
            file_path=os.path.join(self.file_dir, "missing_download.txt"),
            file_type="letter",
        )
        session.add(missing_file)
        session.commit()
        session.refresh(missing_file)
        missing_file_id = missing_file.id
        session.close()

        jwt = generate_jwt(self.user_id, secret=SECRET_KEY)
        res = self.client.get(
            f"/api/v1/file/download/{missing_file_id}", headers={"access_token": jwt}
        )
        self.assertEqual(res.status_code, 404)
