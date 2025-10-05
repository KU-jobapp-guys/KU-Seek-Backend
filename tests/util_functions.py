"""Module containing utility functions for use with unittest."""

from datetime import datetime, timedelta, UTC
from jwt import encode
from controllers.models import User, Company, Student, Job, Terms, Tags


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
    
    student_user1 = User(
        google_uid="55555",
        email="student1@gmail.com",
        type="Student"
    )
    session.add(student_user1)
    session.commit()
    student_user1 = session.query(User).where(User.google_uid == "55555").one()
    cls.student_user1_id = student_user1.id

    student_user2 = User(
        google_uid="66666",
        email="student2@gmail.com",
        type="Student"
    )
    session.add(student_user2)
    session.commit()
    student_user2 = session.query(User).where(User.google_uid == "66666").one()
    cls.student_user2_id = student_user2.id


    # Add temporary company data for testing
    company = Company(
        user_id=cls.user1_id,
        company_name="TechCorp Ltd.",
        company_type="Private",
        company_industry="Software",
        company_size="200-500",
        company_website="https://www.techcorp.com",
        full_location="Bangkok, Thailand"
    )

    company_2 = Company(
        user_id=cls.user2_id,
        company_name="For the Darksouls",
        company_type="Private",
        company_industry="Bodyguard",
        company_size="20-45",
        company_website="https://www.protect-you.com",
        full_location="Chiangmai, Thailand"
    )
    
    session.add(company)
    session.add(company_2)
    session.commit()


    student1 = Student(
        user_id=cls.student_user1_id,
        nisit_id="6401010101",
        education_id=None,
        gpa=3.75,
        interests="AI, Machine Learning, Backend Development"
    )

    student2 = Student(
        user_id=cls.student_user2_id,
        nisit_id="6401010102",
        education_id=None,
        gpa=3.25,
        interests="Frontend Development, UX Design"
    )

    session.add_all([student1, student2])
    session.commit()

    # add tag mock data
    tag_mock_data = [
        'Artificial Intelligence',
        'Web Development',
        'Data Science',
        'Cybersecurity',
        'Cloud Computing',
        'Machine Learning',
        'Blockchain',
        'Mobile Apps'
    ]
    
    for tag_name in tag_mock_data:
        tag = Tags(
            name=tag_name
        )

        session.add(tag)

    session.commit()

    term_mock_data = [
        ('Internship', 'Opportunity'),
        ('Scholarship', 'Opportunity'),
        ('Full-time', 'Job'),
        ('Part-time', 'Job'),
        ('Remote', 'WorkType'),
        ('Onsite', 'WorkType'),
        ('Research', 'Activity'),
        ('Workshop', 'Activity')
    ]

    for term_data in term_mock_data:
        tag = Terms(
            name=term_data[0],
            type=term_data[1]
        )

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
        work_hours="9:00 AM - 5:00 PM"
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
        work_hours="6:00 AM - 8:00 PM"
    )
    session.add(job1)
    session.add(job2)
    session.commit()

    session.close()