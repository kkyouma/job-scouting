from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing JSearch API...")
    if not settings.JSEARCH_API_KEY.get_secret_value():
        logger.warning("JSEARCH_API_KEY seems to be default or empty. Please check your .env file.")

    criteria = SearchCriteria(
        query="Data Engineer",
        date_posted="today",
        location="cl",
    )

    try:
        client = JSearchClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
