# from sqlalchemy.orm import Session
# from .db_controller import BaseController
# from .models.user_model import User, UserTypes
# from uuid import uuid4
# from datetime import datetime
# from argon2 import PasswordHasher

# ph = PasswordHasher()

# def create_admin(email: str, password: str):
#     session = BaseController().get_session()

#     # hash password
#     hashed_pw = ph.hash(password)

#     admin_user = User(
#         id=uuid4(),
#         google_uid="",
#         email=email,
#         password=hashed_pw,
#         type=UserTypes.ADMIN,
#     )

#     session.add(admin_user)
#     session.commit()
#     session.refresh(admin_user)
#     session.close()

#     print(f"Admin created successfully! ID = {admin_user.id}")

# if __name__ == "__main__":
#     email = 'admin@kuseek.com'
#     password = 'admin123'
#     create_admin(email, password)


# from sqlalchemy.orm import Session
# from .db_controller import BaseController
# from .models.user_model import User, UserTypes
# from .models.profile_model import Profile
# from .models.admin_request_model import UserRequest, RequestStatusTypes
# from uuid import uuid4
# from datetime import datetime
# from argon2 import PasswordHasher

# ph = PasswordHasher()

# def create_user_with_profile(email: str, password: str, first_name: str, last_name: str, user_type: UserTypes):
#     session: Session = BaseController().get_session()

#     # hash password
#     hashed_pw = ph.hash(password)

#     # Create User
#     user = User(
#         id=uuid4(),  # CHAR(32) string
#         google_uid=None,
#         email=email,
#         password=hashed_pw,
#         type=user_type,
#         is_verified=False,
#     )
#     session.add(user)
#     session.flush()

#     # Create Profile
#     profile = Profile(
#         user_id=user.id,
#         first_name=first_name,
#         last_name=last_name,
#         email=email,
#         user_type=user_type.name,
#         is_verified=False,
#     )
#     session.add(profile)

#     # Create UserRequest
#     user_request = UserRequest(
#         user_id=user.id,
#         requested_type=user_type,
#         status=RequestStatusTypes.PENDING,
#         created_at=datetime.utcnow(),
#         verification_document=None,
#     )
#     session.add(user_request)

#     session.commit()
#     session.refresh(user)
#     session.refresh(profile)
#     session.refresh(user_request)
#     session.close()

#     print(f"Created {user_type.name}: {email} | User ID = {user.id}")

# if __name__ == "__main__":
#     users_to_create = [
#         # PROFESSOR
#         {"email": "prof1@example.com", "password": "prof123", "first_name": "Prof", "last_name": "One", "role": UserTypes.PROFESSOR},
#         {"email": "prof2@example.com", "password": "prof123", "first_name": "Prof", "last_name": "Two", "role": UserTypes.PROFESSOR},

#         # STUDENT
#         {"email": "student1@example.com", "password": "student123", "first_name": "Student", "last_name": "One", "role": UserTypes.STUDENT},
#         {"email": "student2@example.com", "password": "student123", "first_name": "Student", "last_name": "Two", "role": UserTypes.STUDENT},

#         # COMPANY
#         {"email": "company1@example.com", "password": "company123", "first_name": "Company", "last_name": "One", "role": UserTypes.COMPANY},
#         {"email": "company2@example.com", "password": "company123", "first_name": "Company", "last_name": "Two", "role": UserTypes.COMPANY},
#     ]

#     for u in users_to_create:
#         create_user_with_profile(
#             email=u["email"],
#             password=u["password"],
#             first_name=u["first_name"],
#             last_name=u["last_name"],
#             user_type=u["role"]
#         )

from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from .db_controller import BaseController
from .models.user_model import Company
from .models.job_model import Job
from .models.admin_request_model import JobRequest


def create_companies_and_jobs():
    session: Session = BaseController().get_session()

    try:
        # Map of user_id to company_name
        companies_data = [
            {
                "user_id": "7a1d3327f23043619238074d40740e61",
                "company_name": "Company One",
            },
            {
                "user_id": "c88a1244cf03483e8f8be602726456ca",
                "company_name": "Company Two",
            },
        ]

        for cdata in companies_data:
            # Create company linked to user_id
            company = Company(
                user_id=uuid.UUID(cdata["user_id"]),
                company_name=cdata["company_name"],
                company_type="Tech",  # example, can customize
                company_industry="Software",
                company_size="50-100",
                company_website=f"https://{cdata['company_name'].replace(' ', '').lower()}.com",
                full_location="Bangkok",
            )
            session.add(company)
            session.flush()  # so company.id is generated

            # Create 3 jobs for this company
            for i in range(1, 4):
                job_title = f"{company.company_name} Job {i}"
                job_description = f"Description for {job_title}."
                salary_min = 20000 + i * 1000
                salary_max = 30000 + i * 1500
                location = "Bangkok"
                work_hours = "Full-time"
                job_type = "On-site"
                job_level = "Junior" if i == 1 else "Mid" if i == 2 else "Senior"
                status = "Open"
                visibility = 1
                capacity = 2
                end_date = datetime.utcnow() + timedelta(days=30)
                created_at = datetime.utcnow()

                job = Job(
                    company_id=company.id,
                    title=job_title,
                    description=job_description,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    location=location,
                    work_hours=work_hours,
                    job_type=job_type,
                    job_level=job_level,
                    status=status,
                    visibility=visibility,
                    capacity=capacity,
                    end_date=end_date,
                    created_at=created_at,
                )
                session.add(job)
                session.flush()  # so job.id is generated

                # Create pending JobRequest for each job
                job_request = JobRequest(
                    job_id=job.id,
                    status="PENDING",
                    created_at=created_at,
                    denial_reason=None,
                    approved_at=None,
                    approved_by=None,
                )
                session.add(job_request)

        session.commit()
        print("Companies, Jobs, and JobRequests created successfully.")

    except Exception as e:
        session.rollback()
        print("Error:", e)
    finally:
        session.close()


if __name__ == "__main__":
    create_companies_and_jobs()
