from src.config import settings
from src.models import JobListing
from src.services.notifier import TelegramNotifier
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing Telegram Notification...")
    if not settings.TELEGRAM_BOT_TOKEN.get_secret_value() or "your_" in settings.TELEGRAM_BOT_TOKEN.get_secret_value():
        logger.error("TELEGRAM_BOT_TOKEN seems to be default or empty.")
    # Create dummy jobs
    dummy_jobs = [
        JobListing(
            id="test-1",
            title="Test Job - Python Dev",
            company_name="Test Corp",
            location="Remote",
            url="https://example.com/job1",
            source="Test",
            tags=["Remote", "Python"],
        ),
        JobListing(
            id="test-2",
            title="Test Job - Data Scientist",
            company_name="Data Inc",
            location="New York",
            url="https://example.com/job2",
            source="Test",
            tags=["On-site", "AI"],
        ),
    ]

    try:
        notifier = TelegramNotifier()
        logger.info(f"Sending notification for {len(dummy_jobs)} test jobs to Chat ID: {settings.TELEGRAM_CHAT_ID}...")
        notifier.notify(dummy_jobs)
        logger.info("Notification sent successfully (check your Telegram).")

    except Exception as e:
        logger.error(f"FAILED: {e}")


if __name__ == "__main__":
    main()
