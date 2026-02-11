from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def check_jsearch(criteria: SearchCriteria) -> list[JobListing]:
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


if __name__ == "__main__":
    check_jsearch(SearchCriteria(query="Data Engineer"))
