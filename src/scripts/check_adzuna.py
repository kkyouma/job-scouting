from src.clients.adzuna import AdzunaClient
from src.config import settings
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def check_adzuna(criteria: SearchCriteria):
    logger.info("Testing Adzuna API...")
    if not settings.ADZUNA_APP_ID or "your_" in settings.ADZUNA_APP_ID:
        logger.warning("ADZUNA_APP_ID seems to be default or empty.")
    if not settings.ADZUNA_API_KEY.get_secret_value() or "your_" in settings.ADZUNA_API_KEY.get_secret_value():
        logger.warning("ADZUNA_API_KEY seems to be default or empty.")

    try:
        client = AdzunaClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

        return jobs
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    ...
