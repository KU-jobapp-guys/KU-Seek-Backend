"""Module for testing models."""

from base_test import SimpleTestCase
from controllers.models import Task


class ModelTestCase(SimpleTestCase):
    """Test case for models."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_task_model(self):
        """Test the task ORM model."""
        session = self.database.get_session()
        task = Task(name="testing task")
        session.add(task)
        session.commit()
        task = session.query(Task).where(Task.name == "testing task").one_or_none()
        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, "testing task")
        session.close()
