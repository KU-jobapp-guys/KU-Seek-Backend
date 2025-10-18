"""Module containing utility functions for use with unittest."""

import uuid
from datetime import datetime, date, timedelta, UTC
from jwt import encode

from controllers.models import User, Company, Student, Job, Terms, Tags, Professor


def generate_jwt(uid, iat=None, exp=None, secret="KU-Seek"):
    """Generate a JWT with the given fields."""
    if not iat:
        iat = int(datetime.now(UTC).timestamp())

    if not exp:
        exp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

    payload = {"uid": str(uid), "iat": iat, "exp": exp}

    return encode(payload, secret, algorithm="HS512")


def add_mockup_data(cls):
    """Add mockup data to the test database."""
    # create 2 users in the database
    session = cls.database.get_session()
    user = User(google_uid="12345", email="faker@gmail.com", type="Company")
    session.add(user)
    session.commit()
    user = session.query(User).where(User.google_uid == "12345").one()
    cls.user1_id = user.id

    user = User(google_uid="98765", email="h@kc3r@gmail.com", type="Company")
    session.add(user)
    session.commit()
    user = session.query(User).where(User.google_uid == "98765").one()
    cls.user2_id = user.id

    user3 = User(google_uid="11111", email="company3@gmail.com", type="Company")
    session.add(user3)
    session.commit()
    user3 = session.query(User).where(User.google_uid == "11111").one()
    cls.user3_id = user3.id

    user4 = User(google_uid="22222", email="company4@gmail.com", type="Company")
    session.add(user4)
    session.commit()
    user4 = session.query(User).where(User.google_uid == "22222").one()
    cls.user4_id = user4.id

    user5 = User(google_uid="33333", email="company5@gmail.com", type="Company")
    session.add(user5)
    session.commit()
    user5 = session.query(User).where(User.google_uid == "33333").one()
    cls.user5_id = user5.id

    user6 = User(google_uid="44444", email="company6@gmail.com", type="Company")
    session.add(user6)
    session.commit()
    user6 = session.query(User).where(User.google_uid == "44444").one()
    cls.user6_id = user6.id

    user7 = User(google_uid="00000", email="company7@gmail.com", type="Company")
    session.add(user7)
    session.commit()
    user7 = session.query(User).where(User.google_uid == "00000").one()
    cls.user7_id = user7.id

    student_user1 = User(google_uid="55555", email="student1@gmail.com", type="Student")
    session.add(student_user1)
    session.commit()
    student_user1 = session.query(User).where(User.google_uid == "55555").one()
    cls.student_user1_id = student_user1.id

    student_user2 = User(google_uid="66666", email="student2@gmail.com", type="Student")
    session.add(student_user2)
    session.commit()
    student_user2 = session.query(User).where(User.google_uid == "66666").one()
    cls.student_user2_id = student_user2.id

    professor_user1 = User(
        google_uid="77777", email="professor1@gmail.com", type="Professor"
    )
    session.add(professor_user1)
    session.commit()
    professor_user1 = session.query(User).where(User.google_uid == "77777").one()
    cls.professor_user1_id = professor_user1.id

    professor_user2 = User(
        google_uid="88888", email="professor2@gmail.com", type="Professor"
    )
    session.add(professor_user2)
    session.commit()
    professor_user2 = session.query(User).where(User.google_uid == "88888").one()
    cls.professor_user2_id = professor_user2.id

    professor_user3 = User(
        google_uid="99999", email="professor3@gmail.com", type="Professor"
    )
    session.add(professor_user3)
    session.commit()
    professor_user3 = session.query(User).where(User.google_uid == "99999").one()
    cls.professor_user3_id = professor_user3.id

    # Add temporary company data for testing
    company = Company(
        user_id=cls.user1_id,
        company_name="TechCorp Ltd.",
        company_type="Private",
        company_industry="Software",
        company_size="200-500",
        company_website="https://www.techcorp.com",
        full_location="Bangkok, Thailand",
    )

    company_2 = Company(
        user_id=cls.user2_id,
        company_name="For the Darksouls",
        company_type="Private",
        company_industry="Bodyguard",
        company_size="20-45",
        company_website="https://www.protect-you.com",
        full_location="Chiangmai, Thailand",
    )

    company_3 = Company(
        user_id=cls.user3_id,
        company_name="DataVision Analytics",
        company_type="Public",
        company_industry="Data Science",
        company_size="500-1000",
        company_website="https://www.datavision.com",
        full_location="Phuket, Thailand",
    )

    company_4 = Company(
        user_id=cls.user4_id,
        company_name="CloudNext Solutions",
        company_type="Private",
        company_industry="Cloud Computing",
        company_size="100-200",
        company_website="https://www.cloudnext.io",
        full_location="Chonburi, Thailand",
    )

    company_5 = Company(
        user_id=cls.user5_id,
        company_name="AI Innovations Lab",
        company_type="Startup",
        company_industry="Artificial Intelligence",
        company_size="10-50",
        company_website="https://www.aiinnovations.tech",
        full_location="Bangkok, Thailand",
    )

    company_6 = Company(
        user_id=cls.user6_id,
        company_name="CyberShield Security",
        company_type="Private",
        company_industry="Cybersecurity",
        company_size="50-100",
        company_website="https://www.cybershield.net",
        full_location="Pattaya, Thailand",
    )

    company_7 = Company(
        user_id=cls.user7_id,
        company_name="GreenTech Energy",
        company_type="Public",
        company_industry="Renewable Energy",
        company_size="1000+",
        company_website="https://www.greentech-energy.com",
        full_location="Nakhon Ratchasima, Thailand",
    )

    session.add_all(
        [company, company_2, company_3, company_4, company_5, company_6, company_7]
    )
    session.commit()

    student1 = Student(
        user_id=cls.student_user1_id,
        nisit_id="6401010101",
        education_id=None,
        gpa=3.75,
        interests="AI, Machine Learning, Backend Development",
    )

    student2 = Student(
        user_id=cls.student_user2_id,
        nisit_id="6401010102",
        education_id=None,
        gpa=3.25,
        interests="Frontend Development, UX Design",
    )

    session.add_all([student1, student2])
    session.commit()

    # Add Professor data
    professor1 = Professor(
        user_id=cls.professor_user1_id,
        department="Computer Science",
        position="Associate Professor",
        office_location="Engineering Building, Room 301",
        education_id=None,
        research_interests="Artificial Intelligence," \
        " Machine Learning, Natural Language Processing",
        description="Experienced researcher in AI" \
        " with over 10 years of teaching experience.",
    )

    professor2 = Professor(
        user_id=cls.professor_user2_id,
        department="Software Engineering",
        position="Assistant Professor",
        office_location="Engineering Building, Room 405",
        education_id=None,
        research_interests="Software Architecture, Cloud Computing, DevOps",
        description="Specializes in scalable software" \
        " systems and modern development practices.",
    )

    professor3 = Professor(
        user_id=cls.professor_user3_id,
        department="Data Science",
        position="Professor",
        office_location="Science Building, Room 201",
        education_id=None,
        research_interests="Big Data Analytics, Deep Learning, Computer Vision",
        description="Leading expert in data science with" \
        " multiple published papers in top-tier conferences.",
    )

    session.add_all([professor1, professor2, professor3])
    session.commit()

    # add tag mock data
    tag_mock_data = [
        "Artificial Intelligence",
        "Web Development",
        "Data Science",
        "Cybersecurity",
        "Cloud Computing",
        "Machine Learning",
        "Blockchain",
        "Mobile Apps",
    ]

    for tag_name in tag_mock_data:
        tag = Tags(name=tag_name)
        session.add(tag)

    session.commit()

    term_mock_data = [
        ("Internship", "Opportunity"),
        ("Scholarship", "Opportunity"),
        ("Full-time", "Job"),
        ("Part-time", "Job"),
        ("Remote", "WorkType"),
        ("Onsite", "WorkType"),
        ("Research", "Activity"),
        ("Workshop", "Activity"),
    ]

    for term_data in term_mock_data:
        tag = Terms(name=term_data[0], type=term_data[1])
        session.add(tag)

    session.commit()

    # mockup job data
    job1 = Job(
        capacity=2,
        company_id=1,
        description="Job 1",
        end_date="2025-12-31 23:59:59",
        job_level="Senior-level",
        job_type="full-time",
        location="Bangkok, Thailand",
        salary_max=120000,
        salary_min=80000,
        title="Senior Python Developer",
        work_hours="9:00 AM - 5:00 PM",
    )
    job2 = Job(
        capacity=4,
        company_id=2,
        description="Job 2",
        end_date="2026-08-06 23:59:59",
        job_level="Junior-level",
        job_type="full-time",
        location="Osaka, Japan",
        salary_max=20000,
        salary_min=15000,
        title="Junior Slave Developer",
        work_hours="6:00 AM - 8:00 PM",
    )
    session.add_all([job1, job2])
    session.commit()

    session.close()


def fake_uuid(mock_uid="12345678-1234-5678-1234-567812345678"):
    """Generate a deterministic fake UUID."""
    return uuid.UUID(mock_uid)


def fake_datetime():
    """Generate a fake datetime."""
    return datetime(2025, 1, 1, 12, 0, 0)


def fake_date():
    """Generate a fake date."""
    return date(2025, 1, 1)
