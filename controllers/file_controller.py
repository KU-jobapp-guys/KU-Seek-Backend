"""Module containing endpoints for file serving."""

import os
from flask import send_file
from uuid import UUID
from jwt import decode
from .decorators import role_required
from flask import request
from decouple import config, Csv
from sqlalchemy.orm import joinedload
from swagger_server.openapi_server import models
from werkzeug.utils import secure_filename
from .models.job_model import Job, JobApplication
from .models.user_model import Student, Company
from .models.file_model import File



class FileController:
    """Class for handling file serving."""

    def __init__(self):
        """Initialize the class."""
        self.base_path = config("BASE_FILE_PATH", default="content")

    def get_file(self, file_id:str):
        """Return a file for viewing in the browser."""
        pass

    def download_file(self, file_id:str):
        """Return a file for downloading."""
        pass
