from src.clients.getonboard import GetOnBoardClient
from src.models import SearchCriteria
from src.services.storage_service import save_jobs
from src.util.logger_config import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    criteria = SearchCriteria(query="Data Engineer")

    try:
        client = GetOnBoardClient()
        jobs = client.search_jobs(criteria)

        save_jobs(jobs)

    except Exception as e:
        logger.error(e)
