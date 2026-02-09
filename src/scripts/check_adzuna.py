import logging

from src.clients.adzuna import AdzunaClient
from src.config import settings
from src.models import SearchCriteria

logger = logging.getLogger(__name__)


def main():
    logger.info("Testing Adzuna API...")
    if not settings.ADZUNA_APP_ID or "your_" in settings.ADZUNA_APP_ID:
        print("WARNING: ADZUNA_APP_ID seems to be default or empty.")
    if not settings.ADZUNA_API_KEY.get_secret_value() or "your_" in settings.ADZUNA_API_KEY.get_secret_value():
        print("WARNING: ADZUNA_API_KEY seems to be default or empty.")

    criteria = SearchCriteria(
        query="Python Developer",
        location="us",  # Adzuna needs precise location codes often, defaulting to 'us' in client for now logic
    )

    try:
        client = AdzunaClient()
        jobs = client.search_jobs(criteria)

        print(f"\nFound {len(jobs)} jobs.")
        for job in jobs[:3]:
            print(f"- {job.title} at {job.company_name} ({job.location})")
            print(f"  URL: {job.url}")
            print("-" * 20)

    except Exception as e:
        print(f"FAILED: {e}")


if __name__ == "__main__":
    main()
