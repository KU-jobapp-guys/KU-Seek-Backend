"""Module for testing the instantiation of the ORM and accessing its attributes."""

from datetime import datetime
from decouple import config
from base_test import RoutingTestCase
from util_functions import fake_uuid, fake_datetime, fake_date
from controllers.models import (
    Job,
    JobSkills,
    JobTags,
    JobApplication,
    Bookmark,
    Profile,
    ProfileSkills,
    Education,
    StudentDocuments,
    StudentHistories,
    ProfessorConnections,
    Announcements,
    Tags,
    Terms,
    Token,
    User,
    Student,
    Professor,
    Company,
)


SECRET_KEY = config("SECRET_KEY", default="very-secure-crytography-key")


class ORMTestCase(RoutingTestCase):
    """Test case for testing the instantiation of the ORM and accessing its attributes."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database for this test suite."""
        super().tearDownClass()

    def test_job_model(self):
        """Test Job model instantiation, and access it value."""
        job = Job(
            company_id=1,
            description="Backend developer",
            title="Python Developer",
            salary_min=20000,
            salary_max=40000,
            location="Bangkok",
            work_hours="Full-time",
            job_type="Onsite",
            job_level="Junior",
            capacity=5,
            end_date=fake_datetime(),
            approved_by=None,
        )
        assert job.title == "Python Developer"
        assert job.salary_min == 20000.0

    def test_job_skills_model(self):
        """Test JobSkills model instantiation, and access it value."""
        job_skill = JobSkills(job_id=1, skill_id=2)
        assert job_skill.job_id == 1
        assert job_skill.skill_id == 2

    def test_job_tags_model(self):
        """Test JobTags model instantiation, and access it value."""
        job_tag = JobTags(job_id=1, tag_id=10)
        assert job_tag.tag_id == 10

    def test_job_application_model(self):
        """Test JobApplication model instantiation and attribute access."""
        app = JobApplication(
            job_id=1,
            student_id=2,
            resume="resume.pdf",
            letter_of_application="cover.pdf",
            phone_number="0812345678",
        )
        assert app.resume.endswith(".pdf")
   

    def test_bookmark_model(self):
        """Test Bookmark model instantiation, and access it value."""
        bookmark = Bookmark(job_id=1, student_id=2)
        assert bookmark.job_id == 1
        assert bookmark.student_id == 2

   