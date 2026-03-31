from src.models import JobListing
from src.services.ai_service import AIService
from src.util.logger_config import get_logger

logger = get_logger(__name__)

jobs: list[JobListing] = []


def check_ai():
    ai_service = AIService()
    selected_jobs = ai_service.evaluate_jobs(jobs)

    return selected_jobs


if __name__ == "__main__":
    check_ai()
