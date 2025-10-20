"""Module for admin verification systems."""

import pathlib
import mimetypes
from abc import ABC, abstractmethod
from typing import Any, Dict
from google import genai
from decouple import config


class AdminModel(ABC):
    """Abstract admin class."""

    @abstractmethod
    def verify_user(self, *args, **kwargs):
        """Verify a user's identify."""
        raise NotImplementedError

    @abstractmethod
    def verify_job_post(self, job_post_data: Dict[str, Any]):
        """Verify a job post's validity based on its data."""
        raise NotImplementedError


class YesManModel(AdminModel):
    """Basic auto approve admin model for testing."""

    def __init__(self):
        """Initialize the class."""
        pass

    def verify_user(self, user_info: dict, file: str) -> Dict[str, Any]:
        """
        Verify a user's identify, based on the given file.

        Automatically assumes the user's info and verification document is real.
        and assigns the user role based on the given KU ID if they are student,
        professor, or staff in the case of a KU personel.
        Defaults to student as a fallback.

        Args:
            user_info: the user's info
            file: the file path for the file in the system.

        returns: the user's user type and verification status, which is always True.
        """
        if user_info:
            if user_info["type"] == "company":
                return {"status": True, "role": "company"}

            id = user_info["kuId"]
            if id[0] == "1":
                return {"status": True, "role": "professor"}
            elif id[0] == "2":
                return {"status": True, "role": "staff"}
            else:
                return {"status": True, "role": "student"}

        return {"status": True, "role": "student"}

    def verify_job_post(self, job_post_data) -> bool:
        """
        Verify the job post, always.

        Automatically approves the job post, regardless of the content.

        Args:
            job_post_data: The job post's data

        returns: True
        """
        if job_post_data:
            return True

        return True


class AiAdminModel(AdminModel):
    """Agentic AI model for user and content validation."""

    __GEMINI_KEY = config("GEMINI_KEY", default="real-key-trust")

    def __init__(self, prompt_file, model="gemini-2.5-flash"):
        """Initialize the class."""
        self.prompt = prompt_file
        self.client = genai.Client(api_key=self.__GEMINI_KEY)
        self.model = model
        self.chat = self.__initialize_agentic_ai()

    def __read_prompt_file(self):
        """Read the prompt file for context."""
        with open(self.prompt, "r", encoding="utf-8") as file:
            return file.read()

    def __initialize_agentic_ai(self):
        """Setsup the context for the AI."""
        prompt = self.__read_prompt_file()
        cache = self.client.chats.create(
            model=self.model,
            config={
                "system_instruction": prompt,
                "temperature": 0.2,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",
            },
        )
        return cache

    def verify_user(self, user_data, file):
        """
        Verify a user's identify, based on the given user data.

        Validates whether the provided user data makes sense, and determines the user's
        role based on the context of the provided veriification document.

        Args:
            user_data: The user's data inputted on the registration form.
            file: The file path for the file in the system.

        returns: The user's user type and verification status.
        """
        verification_file = pathlib.Path(file)
        file_type = mimetypes.guess_type(file)[0]
        response = self.chat.send_message(
            [
                genai.types.Part.from_bytes(
                    data=verification_file.read_bytes(),
                    mime_type=f"{file_type}",
                ),
                (
                    f"Validate the provided user data that follows this JSON format: {user_data} "
                    "additionally, review the attached verification document."
                ),
            ],
        )

        return response.text

    def verify_job_post(self, job_post_data):
        """
        Verify a job post's validity, based on the given user data.

        Validates whether the provided job post makes sense, determines whether
        the content violates any content rules or is potentially malicious.

        Args:
            job_post_data: The job post data.

        returns: The job post's validity and reason if the job post is not valid.
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                f"Validate the following job post data in JSON format: {job_post_data}"
            ),
            config=genai.types.GenerateContentConfig(cached_content=self.cache.name),
        )
        return response.text
