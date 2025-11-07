"""Module for sending emails."""

import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config

SERVER_EMAIL = config("SERVICE_EMAIL", default="faker@gmail.com")
EMAIL_PW = config("EMAIL_PASSWORD", default="realpw123")


class EmailSender:
    """Class for sending emails via SMTP."""

    def __init__(self):
        """Initialize the class."""
        self.email = SERVER_EMAIL

    def send_email(self, recipient: str, topic: str, email_file: str):
        """
        Send an email to the recipient.

        Sends an email to the provided recipient with the provided topic and body.

        Args:
            recipient: The recipient's email
            topic: The topic/subject to address the email with
            email_file: The file name for the email's body/content
                        without the file extension
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = topic
        msg["From"] = self.email
        msg["To"] = recipient

        email_file = os.path.join(
            os.getcwd(), "controllers", "management", "email_templates", email_file
        )

        try:
            with open(email_file + ".html", "r", encoding="utf-8") as f:
                html_content = f.read()
                html_content = html_content.replace("{{UserName}}", recipient)
        except IOError as e:
            raise IOError("HTML file could not be read.", e)

        try:
            with open(email_file + ".txt", "r", encoding="utf-8") as f:
                text_content = f.read()
                text_content = text_content.replace("{{UserName}}", recipient)
        except IOError as e:
            raise IOError("Plain text file could not be read.", e)

        # Create the body of the message
        text = text_content
        html = html_content

        # Record text/plain and text/html parts,
        # the email will prefer the last provided part
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send the email.
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(SERVER_EMAIL, EMAIL_PW)
                smtp_server.sendmail(self.email, recipient, msg.as_string())
                smtp_server.quit()
        except Exception as e:
            raise ValueError("Email could not be sent.", e)
