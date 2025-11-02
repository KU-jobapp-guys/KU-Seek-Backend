"""Email scheduler for sending pending notifications."""

import threading
from typing import Optional
from controllers.db_controller import AbstractDatabaseController
from .email_sender import WelcomeEmailStrategy, CompanyNotificationEmailStrategy


class EmailScheduler:
    """Background scheduler for processing and sending pending emails."""

    WELCOME_EMAIL_STRATEGY = WelcomeEmailStrategy()
    COMPANY_EMAIL_STRATEGY = CompanyNotificationEmailStrategy()

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
            try:
                session = self._database.get_session()
                session.close()

            except Exception as e:
                pass

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
