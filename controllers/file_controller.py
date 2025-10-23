"""Module containing endpoints for file serving."""

import os

from flask import send_from_directory
from .decorators import login_required
from decouple import config
from swagger_server.openapi_server import models
from .models.file_model import File


FILE_DIR = config("BASE_FILE_PATH", default="content")


class FileController:
    """Class for handling file serving."""

    def __init__(self, database):
        """Initialize the class."""
        self.db = database
        self.base_path = os.path.join(os.getcwd(), FILE_DIR)

    @login_required
    def get_file(self, file_id: str):
        """
        Return a file for viewing in the browser.

        Serve a file to the frontend, with the provided file id.
        This method requires authentication.

        Args:
            file_id: The file's UID

        Returns A flask response object, containing the file.
        """
        try:
            session = self.db.get_session()
            file = session.query(File).where(File.id == file_id).one_or_none()
            if not file:
                session.close()
                return models.ErrorMessage("File record not found"), 404
            file_name = file.file_name
            session.close()
        except Exception as e:
            session.close()
            return models.ErrorMessage("Database Error occured: ", e), 400

        try:
            return send_from_directory(self.base_path, file_name, as_attachment=False)
        except FileNotFoundError:
            return models.ErrorMessage("File not found"), 404

    @login_required
    def download_file(self, file_id: str):
        """
        Return a file for downloading.

        Serve a file to the frontend as an attachment, with the provided file id.
        This method requires authentication.

        Args:
            file_id: The file's UID

        Returns A flask response object, containing the file as an attachment.
        """
        try:
            session = self.db.get_session()
            file = session.query(File).where(File.id == file_id).one_or_none()
            if not file:
                session.close()
                return models.ErrorMessage("File record not found"), 404
            file_name = file.file_name
            session.close()
        except Exception as e:
            session.close()
            return models.ErrorMessage("Database Error occured: ", e), 400

        try:
            return send_from_directory(self.base_path, file_name, as_attachment=True)
        except FileNotFoundError:
            return models.ErrorMessage("File not found"), 404
