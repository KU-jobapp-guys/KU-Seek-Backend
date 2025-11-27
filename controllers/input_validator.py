"""Input validation controller."""

import re
import uuid
from datetime import datetime, date, timezone
from .models.job_model import Job, JobApplication
from .models.user_model import Student, Company


class InputValidator:
    @classmethod
    def job_post(cls, db_session, user_id, body):
        """Validate job post payload.

        Returns:
            cleaned on success
            ValueError(error_message) on failure
        """

        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format. Expected UUID string.")
            
        company_obj = (
            db_session.query(Company).where(Company.user_id == user_id).one_or_none()
        )

        if not company_obj:
            raise ValueError(
                "Company not found for current user. Create a company first."
            )

        required_fields = [
            "title",
            "salary_min",
            "salary_max",
            "location",
            "work_hours",
            "job_type",
            "job_level",
            "capacity",
            "end_date",
        ]

        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        cleaned = dict(body)

        str_fields = ["title", "location", "work_hours", "job_type", "job_level"]
        for f in str_fields:
            val = cleaned.get(f)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"Field '{f}' must be a non-empty string")
            cleaned[f] = val.strip()

        try:
            salary_min = float(cleaned.get("salary_min"))
            salary_max = float(cleaned.get("salary_max"))
        except (TypeError, ValueError):
            raise ValueError("Fields 'salary_min' and 'salary_max' must be numeric")

        if salary_min < 0 or salary_max < 0:
            raise ValueError("Salary values must be non-negative")

        if salary_min > salary_max:
            raise ValueError("Field 'salary_min' cannot be greater than 'salary_max'")

        cleaned["salary_min"] = salary_min
        cleaned["salary_max"] = salary_max

        try:
            capacity = int(cleaned["capacity"])
        except (TypeError, ValueError):
            raise ValueError("Field 'capacity' must be an integer")

        if capacity <= 0:
            raise ValueError("Field 'capacity' must be greater or equal to 1")

        cleaned["capacity"] = capacity

        now = datetime.now(timezone.utc)
        end_date = body["end_date"]

        try:
            if isinstance(end_date, str):
                cleaned["end_date"] = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            raise ValueError("Field 'end_date' must be a date or ISO date string")
        
        if cleaned["end_date"] < now:
            raise ValueError("Field 'end_date' must be in the future")

        cleaned["company_obj"] = company_obj

        return cleaned
        

    @classmethod
    def job_application(cls, db_session, user_id, job_id, body):
        """Validate job application payload.

        Returns:
            cleaned on success
            ValueError(error_message) on failure
        """

        job = db_session.query(Job).where(Job.id == job_id).one_or_none()
        current_applicants = (
            db_session.query(JobApplication).where(JobApplication.job_id == job_id).all()
        )

        student = (
            db_session.query(Student)
            .where(Student.user_id == uuid.UUID(user_id))
            .one_or_none()
        )

        if not job:
            raise ValueError("Job not found.")

        if not student:
            raise ValueError("Student not found")

        if not len(current_applicants) < job.capacity:
            raise ValueError("Invalid job provided.")
        
        if str(student.id) in [
            str(applicant.student_id) for applicant in current_applicants
        ]:
            raise ValueError("Could not create job application.")

        required_fields = [
            "first_name",
            "last_name",
            "email",
            "years_of_experience",
            "expected_salary",
            "phone_number",
        ]

        for field in required_fields:
            if field not in body:
                raise ValueError(f"Missing required field: {field}")

        cleaned = dict(body)

        for f in ["first_name", "last_name"]:
            val = cleaned.get(f)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"Field '{f}' must be a non-empty string")
            cleaned[f] = val.strip()

        email = cleaned.get("email")
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Field 'email' must be a non-empty string")
        email = email.strip()
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Field 'email' must be a valid email address")
        cleaned["email"] = email

        try:
            years = int(cleaned.get("years_of_experience"))
        except (TypeError, ValueError):
            raise ValueError("Field 'years_of_experience' must be an integer")

        if years < 0:
            raise ValueError("Field 'years_of_experience' must be non-negative")
        cleaned["years_of_experience"] = years

        try:
            salary = float(cleaned.get("expected_salary"))
        except (TypeError, ValueError):
            raise ValueError("Field 'expected_salary' must be numeric")  

        if salary < 0:
            raise ValueError("Field 'expected_salary' must be non-negative")

        cleaned["expected_salary"] = float(salary)

        phone = cleaned.get("phone_number")
        if not isinstance(phone, str) or not re.fullmatch(r"\d{9,}", phone):
            raise ValueError("Field 'phone_number' must be a non-empty string with at least 9 characters")
        cleaned["phone_number"] = phone.strip()

        cleaned['job'] = job
        cleaned['student'] = student

        return cleaned
    

    @classmethod
    def student_registration(cls, body):
        """Validate student registration payload.

        Returns:
            cleaned on success
            ValueError(err_msg) on failure
        """
        cleaned = dict(body)

        nisit_id = cleaned.get("kuId")
        if not isinstance(nisit_id, str) or not re.fullmatch(r"\d{10}", nisit_id):
            raise ValueError("Field 'kuId' must be a numeric string with length 10")
        cleaned["kuId"] = nisit_id.strip()

        return cleaned
    

    @classmethod
    def company_registration(cls, body):
        """Validate company registration payload.

        Returns:
            cleaned on success
            ValueError(err_msg) on failure
        """
        required_fields = ["companyName", "companySize"]

        for field in required_fields:
            if field not in body:
                raise ValueError(f"Missing required field: {field}")

        cleaned = dict(body)

        company_name = cleaned.get("companyName")
        if not isinstance(company_name, str) or not company_name.strip():
            raise ValueError("Field 'companyName' must be a non-empty string")
        cleaned["companyName"] = company_name.strip()

        valid_sizes = [
            'less than 100',
            '101 - 1,000',
            '1,001 - 10,000',
            'more than 10,000'
        ]

        company_size = cleaned.get("companySize")
        if not isinstance(company_size, str) or not company_size.strip() or company_size not in valid_sizes:
            raise ValueError("Field 'companySize' must be a non-empty string and one of the valid sizes")
        cleaned["companySize"] = company_size.strip()

        return cleaned


    @classmethod
    def professor_registration(cls, body):
        """Validate professor profile payload.
        Nothing to validate yet during registration.

        Returns:
            body
        """
        return body
    
    @classmethod
    def register(cls, user_type, body):
        """Validate registration payload based on user_type.
        Returns:
            cleaned on success
            ValueError(err_msg) on failure
        """
        required_keys = ["google_uid", "email", "user_type"]
        valid_keys = all(key in body for key in required_keys)
        if not valid_keys:
            raise TypeError("Invalid credentials.")

        match user_type:
            case "student":
                return cls.student_registration(body)
            case "company":
                return cls.company_registration(body)
            case "professor":
                return cls.professor_registration(body)
            case _:
                raise ValueError("Invalid user_type.")
