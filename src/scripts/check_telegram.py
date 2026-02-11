from src.config import settings
from src.models import JobListing
from src.services.notifier import TelegramNotifier
from src.services.storage_service import get_unnotified_jobs
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def check_notify(jobs: list[JobListing]):
    logger.info("Testing Telegram Notification")
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN seems to be empty.")

    try:
        notifier = TelegramNotifier()
        logger.info(f"Sending notification for {len(jobs)} test jobs to Chat ID: {settings.TELEGRAM_CHAT_ID}")
        notifier.notify(jobs)
        logger.info("Notification sent successfully.")

    except Exception as e:
        logger.error(f"FAILED: {e}")


if __name__ == "__main__":
    check_notify(jobs=get_unnotified_jobs())
