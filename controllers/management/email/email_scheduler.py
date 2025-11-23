"""Email scheduler for sending pending notifications."""

import threading
import os

from typing import Optional
from controllers.db_controller import AbstractDatabaseController
from controllers.models.email_model import (
    MailRecord,
    MailQueue,
    MailStatus,
)
from .email_sender import GmailEmailStrategy, EmailSender


class EmailScheduler:
    """Background scheduler for processing and sending pending emails."""

    def __init__(
        self, database: AbstractDatabaseController, interval_seconds: int = 300
    ):
        """
        Initialize email scheduler.

        Args:
            database: The dedicated database controller/connection
            interval_seconds: Time between email processing runs (default: 5 minutes)
        """
        self.interval_seconds = interval_seconds
        self._stop_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._is_running = False
        self._database = database

    def _worker(self):
        """Background worker that processes emails at regular intervals."""
        # TODO: Integrate logging
        while not self._stop_flag.is_set():
            # this should REALLY be a log in the logfile but no logger :(
            print("Running email batch job", flush=True)
            try:
                session = self._database.get_session()

                gmail_strategy = GmailEmailStrategy()
                email_sender = EmailSender(gmail_strategy)

                # resend failed emails with retry_count < 3
                failed_emails = (
                    session.query(MailRecord)
                    .filter(
                        MailRecord.status.in_(
                            [MailStatus.MAILWAIT, MailStatus.MAILSOFTERROR]
                        ),
                        MailRecord.retry_count < 3,
                    )
                    .all()
                )

                for mail_record in failed_emails:
                    try:
                        # Attempt to resend using raw body content
                        email_sender.send_email_raw(
                            recipient=mail_record.recipient,
                            topic=mail_record.topic,
                            text_body=mail_record.text_body,
                            html_body=mail_record.html_body,
                        )

                        # Mark as sent
                        mail_record.status = MailStatus.MAILSENT
                        session.commit()

                    except Exception:
                        mail_record.retry_count += 1

                        # On 3rd retry failure, mark as hard error
                        if mail_record.retry_count >= 3:
                            mail_record.status = MailStatus.MAILHARDERROR
                        else:
                            mail_record.status = MailStatus.MAILSOFTERROR

                        session.commit()

                # process mail queue
                queued_emails = session.query(MailQueue).all()

                for queued_mail in queued_emails:
                    try:
                        template_args = [
                            (param.key, param.value) for param in queued_mail.parameters
                        ]

                        # Send the email using template
                        email_sender.send_email(
                            recipient=queued_mail.recipient,
                            topic=queued_mail.topic,
                            email=queued_mail.template,
                            template_args=template_args,
                        )

                        # Get the rendered content for the mail record
                        # Read and render templates to store in mail record
                        email_file = os.path.join(
                            os.getcwd(),
                            "controllers",
                            "management",
                            "email",
                            "email_templates",
                            queued_mail.template,
                        )

                        with open(email_file + ".html", "r", encoding="utf-8") as f:
                            html_body = f.read()
                            html_body = html_body.replace(
                                "{{UserName}}", queued_mail.recipient
                            )
                            for param in template_args:
                                html_body = html_body.replace(
                                    "{{" + param[0] + "}}", param[1]
                                )

                        with open(email_file + ".txt", "r", encoding="utf-8") as f:
                            text_body = f.read()
                            text_body = text_body.replace(
                                "{{UserName}}", queued_mail.recipient
                            )
                            for param in template_args:
                                html_body = html_body.replace(
                                    "{{" + param[0] + "}}", param[1]
                                )

                        # Create a mail record for successful send
                        mail_record = MailRecord(
                            recipient=queued_mail.recipient,
                            topic=queued_mail.topic,
                            text_body=text_body,
                            html_body=html_body,
                            status=MailStatus.MAILSENT,
                            retry_count=0,
                        )
                        session.add(mail_record)

                        # Remove from queue
                        session.delete(queued_mail)
                        session.commit()

                    except Exception as e:
                        print(f"Error: {e}", flush=True)
                        # Store template path if rendering failed
                        mail_record = MailRecord(
                            recipient=queued_mail.recipient,
                            topic=queued_mail.topic,
                            text_body=text_body,
                            html_body=html_body,
                            status=MailStatus.MAILSOFTERROR,
                            retry_count=1,
                        )
                        session.add(mail_record)

                        # Remove from queue
                        session.delete(queued_mail)
                        session.commit()

                session.close()
                print("Finished email batch job", flush=True)

            except Exception:
                # Log exception when its real
                if "session" in locals():
                    session.rollback()
                    session.close()

            # Sleep for the interval, but check stop flag periodically
            self._stop_flag.wait(timeout=self.interval_seconds)

    def start(self):
        """Start the email scheduler in a background thread."""
        if self._is_running:
            return

        self._stop_flag.clear()
        self._thread = threading.Thread(
            target=self._worker, name="EmailSchedulerThread", daemon=True
        )
        self._thread.start()
        self._is_running = True

    def stop(self, timeout: int = 10):
        """
        Stop the email scheduler gracefully.

        Args:
            timeout: Maximum seconds to wait for thread to stop
        """
        if not self._is_running:
            return

        self._stop_flag.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                pass

        self._is_running = False

    def is_running(self) -> bool:
        """Check if scheduler is currently running."""
        return self._is_running and self._thread and self._thread.is_alive()


# Global scheduler instance
_scheduler: Optional[EmailScheduler] = None


def start_email_scheduler(interval_seconds: int = 300) -> EmailScheduler:
    """
    Start the global email scheduler.

    Args:
        interval_seconds: Time between email processing runs (default: 5 minutes)

    Returns:
        The scheduler instance
    """
    global _scheduler

    if _scheduler and _scheduler.is_running():
        return _scheduler

    _scheduler = EmailScheduler(interval_seconds=interval_seconds)
    _scheduler.start()
    return _scheduler


def stop_email_scheduler(timeout: int = 10):
    """
    Stop the global email scheduler.

    Args:
        timeout: Maximum seconds to wait for scheduler to stop
    """
    global _scheduler

    if _scheduler:
        _scheduler.stop(timeout=timeout)


def get_scheduler() -> Optional[EmailScheduler]:
    """Get the global scheduler instance."""
    return _scheduler
