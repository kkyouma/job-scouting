from src.clients.adzuna import AdzunaClient
from src.config import settings
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing Adzuna API...")
    if not settings.ADZUNA_APP_ID or "your_" in settings.ADZUNA_APP_ID:
        logger.warning("ADZUNA_APP_ID seems to be default or empty.")
    if not settings.ADZUNA_API_KEY.get_secret_value() or "your_" in settings.ADZUNA_API_KEY.get_secret_value():
        logger.warning("ADZUNA_API_KEY seems to be default or empty.")

    criteria = SearchCriteria(
        query="Python Developer",
        location="us",  # Adzuna needs precise location codes often, defaulting to 'us' in client for now logic
    )

    try:
        client = AdzunaClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"\nFound {len(jobs)} jobs.")
        for job in jobs[:3]:
            logger.info(f"- {job.title} at {job.company_name} ({job.location})")
            logger.info(f"  URL: {job.url}")
            logger.info("-" * 20)

    except Exception as e:
        logger.error(f"FAILED: {e}")


if __name__ == "__main__":
    main()
