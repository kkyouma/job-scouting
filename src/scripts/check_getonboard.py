from src.clients.getonboard import GetOnBoardClient
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing GetOnBoard API...")
    # GetOnBoard might not need keys for public search, but good to verify

    criteria = SearchCriteria(query="Python", location="Remote")

    try:
        client = GetOnBoardClient()
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
