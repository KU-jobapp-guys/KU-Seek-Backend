"""Module for sending emails."""

import smtplib
import os

from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from decouple import config


SERVER_EMAIL = config("SERVICE_EMAIL", default="faker@gmail.com")
EMAIL_PW = config("EMAIL_PASSWORD", default="realpw123")


class EmailStrategy(ABC):
    """Abstract class for defining email sending strategies."""

    @abstractmethod
    def send_email(self, recipient: str, topic: str, email_file: str):
        """Send an email to a recipient."""
        raise NotImplementedError

    @abstractmethod
    def send_email_raw(
        self, recipient: str, topic: str, text_body: str, html_body: str
    ):
        """Send an email with raw body content."""
        raise NotImplementedError


class GmailEmailStrategy(EmailStrategy):
    """Class for sending emails via Gmail's SMTP."""

    def __init__(self):
        """Initialize the class."""
        self.email = SERVER_EMAIL

    def send_email(
        self,
        recipient: str,
        topic: str,
        email_file: str,
        template_args: list[tuple[str, str]] = [],
    ):
        """
        Send an email to the recipient.

        Sends an email to the provided recipient with the provided topic and
        template body contained in email_file.

        Args:
            recipient: The recipient's email
            topic: The topic/subject to address the email with
            email_file: The file name for the email's body/content
                        without the file extension
            template_args: Tuple containing the template to replace and its value,
                           example: ("{{recipient}}", "faker@gmail.com")
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
                for arg in template_args:
                    html_content = html_content.replace("{{" + arg[0] + "}}", arg[1])
        except IOError as e:
            raise IOError("HTML file could not be read.", e)

        try:
            with open(email_file + ".txt", "r", encoding="utf-8") as f:
                text_content = f.read()
                text_content = text_content.replace("{{UserName}}", recipient)
                for arg in template_args:
                    html_content = html_content.replace("{{" + arg[0] + "}}", arg[1])
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

    def send_email_raw(
        self, recipient: str, topic: str, text_body: str, html_body: str
    ):
        """
        Send an email to the recipient, with raw body content.

        Sends an email to the provided recipient with the provided text and html body.

        Args:
            recipient: The recipient's email
            topic: The topic/subject to address the email with
            text_body: The email body, in plaintext
            html_body: The email body, in HTML5
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = topic
        msg["From"] = self.email
        msg["To"] = recipient

        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
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


class EmailSender:
    """Class for sending Emails."""

    def __init__(self, strategy: EmailStrategy):
        """Initialize the class."""
        self.strategy = strategy

    def send_email(
        self,
        recipient: str,
        topic: str,
        email: str,
        template_args: list[tuple[str, str]],
    ):
        """Send an email to the recipient."""
        self.strategy.send(recipient, topic, email, template_args)

    def send_email_raw(
        self, recipient: str, topic: str, text_body: str, html_body: str
    ):
        """Send an email with raw body content."""
        self.strategy.send(recipient, topic, text_body, html_body)
