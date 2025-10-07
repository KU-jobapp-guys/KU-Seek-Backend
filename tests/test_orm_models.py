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

    def test_profile_model(self):
        """Test Profile model instantiation, and access it value."""
        profile = Profile(
            user_id=fake_uuid(),
            first_name="Banana",
            last_name="Lord",
            email="banana@example.com",
            gender="M",
            age=20,
            user_type="student",
            phone_number="0999999999",
            is_verified=True,
        )
        assert profile.first_name == "Banana"
        assert profile.is_verified is True

    def test_profile_skills_model(self):
        """Test ProfileSkills model instantiation, and access it value."""
        ps = ProfileSkills(user_id=fake_uuid(), skill_id=1)
        assert ps.skill_id == 1

    def test_education_model(self):
        """Test Education model instantiation, and access it value."""
        edu = Education(
            curriculum_name="Computer Engineering",
            university="Kasetsart University",
            major="Software Engineering",
            year_of_study=fake_date(),
            graduate_year=fake_date(),
        )
        assert edu.major == "Software Engineering"

    def test_student_documents_model(self):
        """Test StudentDocuments model instantiation, and access it value."""
        doc = StudentDocuments(
            student_id=fake_uuid(),
            file_path="/files/resume.pdf",
            original_filename="resume.pdf",
        )
        assert doc.original_filename == "resume.pdf"

    def test_student_histories_model(self):
        """Test StudentHistories model instantiation, and access it value."""
        sh = StudentHistories(job_id=1, student_id=fake_uuid())
        assert sh.job_id == 1
        assert sh.student_id is not None

    def test_professor_connections_model(self):
        """Test ProfessorConnections model instantiation, and access it value."""
        pc = ProfessorConnections(
            professor_id=fake_uuid(),
            company_id=fake_uuid("12345678-1234-5678-1234-689723345189"),
        )
        assert pc.professor_id != pc.company_id

    def test_announcements_model(self):
        """Test Annoucements model instantiation, and access it value."""
        ann = Announcements(
            professor_id=fake_uuid(),
            title="Job Fair 2025",
            content="Join us at the main hall!",
        )
        assert "Job Fair" in ann.title

    def test_tags_model(self):
        """Test Tags model instantiation, and access it value."""
        tag = Tags(name="Python")
        assert tag.name == "Python"

    def test_terms_model(self):
        """Test Terms model instantiation, and access it value."""
        term = Terms(name="Backend", type="Skill")
        assert term.type == "Skill"

    