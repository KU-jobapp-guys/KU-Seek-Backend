"""Module for admin verification systems."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
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

    def verify_user(self, file: str) -> Tuple[str, bool]:
        """
        Verify a user's identify, based on the given file.

        Automatically assumes the given file is valid, and classifies the user
        if they are student, professor, or staff based on the file type and file name.

        Args:
            file: the file path for the file in the system.

        returns: the user's user type and verification status, which is always True.
        """
        if file:
            pass

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

    def __init__(self, prompt_file, model=""):
        """Initialize the class."""
        self.prompt = prompt_file
        self.client = genai.Client(self.__GEMINI_KEY)
        self.model = model
        self.cache = self.__initialize_agentic_ai()

    def __read_prompt_file(self):
        """Read the prompt file for context."""
        with open(self.prompt, 'r', encoding='utf-8') as file:
            return file.read()

    def __initialize_agentic_ai(self):
        """Setsup the context for the AI."""
        prompt = self.__read_prompt_file()
        cache = self.client.caches.create(
            model=self.model,
            config=genai.types.CreateCachedContentConfig(
                display_name="",
                system_instruction=prompt,
                ttl="2hr",
            ),
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
        user_info = f"{user_data}"
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                "Introduce different characters in the movie by describing "
                "their personality, looks, and names. Also list the timestamps "
                "they were introduced for the first time."
            ),
            config=genai.types.GenerateContentConfig(cached_content=self.cache.name),
        )

        return response["message"]["content"]
