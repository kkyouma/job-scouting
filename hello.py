from src.clients.adzuna import AdzunaClient
from src.clients.getonboard import GetOnBoardClient
from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, SearchCriteria
from src.services.filter_service import FilterService
from src.services.notifier import TelegramNotifier
from src.services.storage_service import get_all_jobs
from src.util.logger_config import get_logger

logger = get_logger(__name__)

criteria = SearchCriteria(query="Junior Data Engineer", date_posted="today", location="cl")


def test_getonboard(criteria: SearchCriteria) -> list[JobListing]:
    logger.info("Testing GetOnBoard API")

    try:
        client = GetOnBoardClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

    except Exception as e:
        logger.error(e)

    return jobs


def test_adzuna(criteria: SearchCriteria, recent_days: int = 2) -> list[JobListing]:
    logger.info("Testing Adzuna API...")
    if not settings.ADZUNA_APP_ID or "your_" in settings.ADZUNA_APP_ID:
        logger.warning("ADZUNA_APP_ID seems to be default or empty.")
    if not settings.ADZUNA_API_KEY.get_secret_value() or "your_" in settings.ADZUNA_API_KEY.get_secret_value():
        logger.warning("ADZUNA_API_KEY seems to be default or empty.")

    try:
        client = AdzunaClient()
        jobs = client.search_jobs(criteria, recent_days=recent_days)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

    except Exception as e:
        logger.exception(e)

    return jobs


def test_jsearch(criteria: SearchCriteria) -> list[JobListing]:
    logger.info("Testing JSearch API...")
    if not settings.JSEARCH_API_KEY:
        logger.warning("JSEARCH_API_KEY seems to be empty. Please check your .env file.")

    try:
        client = JSearchClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

    except Exception as e:
        logger.error(e)

    return jobs


def test_notifier(jobs: list[JobListing]):
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


def log_jobs(job: JobListing, i: int):
    link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
    logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")


if __name__ == "__main__":
    # jobs = test_getonboard(criteria)
    # jobs = test_jsearch(criteria)
    # logger.debug(jobs[0])

    # logger.info("Saving jobs to database...")
    # save_jobs(jobs)
    # logger.info("Saved jobs to database.")

    # unnotified_jobs = get_unnotified_jobs()
    all_jobs = get_all_jobs()
    filtered_jobs = FilterService.filter_jobs(all_jobs)
    for i, job in enumerate(filtered_jobs[:20]):
        log_jobs(job, i)

    test_notifier(filtered_jobs)

    # ids = [job.id for job in filtered_jobs]
    # mark_jobs_as_notified(ids)
