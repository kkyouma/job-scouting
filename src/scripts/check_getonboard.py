from src.clients.getonboard import GetOnBoardClient
from src.models import SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Testing GetOnBoard API")
    # GetOnBoard might not need keys for public search, but good to verify

    criteria = SearchCriteria(query="Data Engineer")

    try:
        client = GetOnBoardClient()
        jobs = client.search_jobs(criteria)

        logger.info(f"Found {len(jobs)} jobs.")
        for i, job in enumerate(jobs[:20]):
            link = f"\033]8;;{job.url}\033\\Link\033]8;;\033\\"
            logger.info(f"{i + 1}. {job.title} at {job.company_name} ({job.location}) - {link}")

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
