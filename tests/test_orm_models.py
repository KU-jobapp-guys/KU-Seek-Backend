"""Module for testing the instantiation of the ORM and accessing its attributes."""

from datetime import datetime
from decouple import config
from base_test import RoutingTestCase
from util_functions import fake_uuid, fake_datetime, fake_date, add_mockup_data
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
    """Test case for the instantiation of the ORM and accessing its attributes."""

    @classmethod
    def setUpClass(cls):
        """Set up the database for this test suite."""
        super().setUpClass()
        add_mockup_data(cls)

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
            first_name="joe",
            last_name="biden",
            years_of_experience="3 years",
            expected_salary="< 1000",
            contact_email="joebiden@joe.com",
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
            student_id=1,
            file_path="/files/resume.pdf",
            original_filename="resume.pdf",
        )
        assert doc.original_filename == "resume.pdf"

    def test_student_histories_model(self):
        """Test StudentHistories model instantiation, and access it value."""
        sh = StudentHistories(job_id=1, student_id=1)
        assert sh.job_id == 1
        assert sh.student_id is not None

    def test_professor_connections_model(self):
        """Test ProfessorConnections model instantiation, and access it value."""
        pc = ProfessorConnections(
            professor_id=1,
            company_id=2,
        )
        assert pc.professor_id == 1
        assert pc.company_id == 2

    def test_announcements_model(self):
        """Test Annoucements model instantiation, and access it value."""
        ann = Announcements(
            professor_id=1,
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

    def test_token_model(self):
        """Test Token model instantiation, and access it value."""
        token = Token(uid=fake_uuid(), refresh_id=1)
        assert token.refresh_id == 1

    def test_user_model(self):
        """Test User model instantiation, and access it value."""
        user = User(
            google_uid="abc123",
            email="user@example.com",
            is_verified=True,
            type="Student",
        )
        assert user.is_verified
        assert user.email.endswith("@example.com")

    def test_student_model(self):
        """Test Student model instantiation, and access it value."""
        student = Student(
            user_id=fake_uuid(),
            nisit_id="65123456",
            education_id=None,
            gpa=3.75,
            interests="AI, Backend",
        )
        assert float(student.gpa) == 3.75

    def test_professor_model(self):
        """Test Professor model instantiation, and access it value."""
        prof = Professor(
            user_id=fake_uuid(),
            department="Computer Science",
            position="Lecturer",
            office_location="IT Building 3",
            education_id=None,
            research_interests="Machine Learning",
            description="Researcher in ML",
        )
        assert "ML" in prof.description

    def test_company_model(self):
        """Test Company model instantiation, and access it value."""
        comp = Company(
            user_id=fake_uuid(),
            company_name="Banana Corp",
            company_type="Tech",
            company_industry="Software",
            company_size="50-100",
            company_website="https://banana.example.com",
            full_location="Bangkok, Thailand",
        )
        assert comp.company_name == "Banana Corp"

    def test_job_application_defaults(self):
        """Test JobApplication default values."""
        session = self.database.get_session()
        try:
            app = JobApplication(
                job_id=1,
                student_id=2,
                first_name="joe",
                last_name="biden",
                contact_email="joebiden@joe.com",
                years_of_experience="3 years",
                expected_salary="< 1000",
                resume="resume.pdf",
                letter_of_application="cover.pdf",
                phone_number="0812345678",
            )
            session.add(app)
            session.flush()
            assert app.status == "pending"
            assert app.applied_at is not None
        finally:
            session.rollback()
            session.close()

    def test_bookmark_defaults(self):
        """Test Bookmark default values without committing."""
        session = self.database.get_session()
        try:
            bookmark = Bookmark(job_id=1, student_id=2)
            session.add(bookmark)
            session.flush()
            assert isinstance(bookmark.created_at, datetime)
        finally:
            session.rollback()
            session.close()

    def test_student_histories_defaults(self):
        """Test StudentHistories default values without committing."""
        session = self.database.get_session()
        try:
            sh = StudentHistories(job_id=1, student_id=1)
            session.add(sh)
            session.flush()
            assert isinstance(sh.viewed_at, datetime)
        finally:
            session.rollback()
            session.close()
