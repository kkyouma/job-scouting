from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing JSearch API...")
    if not settings.JSEARCH_API_KEY.get_secret_value() or "your_" in settings.JSEARCH_API_KEY.get_secret_value():
        logger.warning("JSEARCH_API_KEY seems to be default or empty. Please check your .env file.")

    criteria = SearchCriteria(query="Python Developer", location="Remote")

    try:
        client = JSearchClient()
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
