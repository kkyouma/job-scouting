from src.clients.getonboard import GetOnBoardClient
from src.models import SearchCriteria
from src.scripts.check_jsearch import check_jsearch
from src.scripts.check_telegram import check_notify
from src.services.storage_service import get_unnotified_jobs, save_jobs
from src.util.logger_config import get_logger

logger = get_logger(__name__)

criteria = SearchCriteria(query="Data Engineer", date_posted="today", location="cl")


def test_getonboard(criteria: SearchCriteria):
    try:
        client = GetOnBoardClient()
        jobs = client.search_jobs(criteria, per_page=5)
        save_jobs(jobs)

    except Exception as e:
        logger.error(e)


def test_jsearch(criteria: SearchCriteria):
    try:
        jobs = check_jsearch(criteria)
        save_jobs(jobs)

    except Exception as e:
        logger.error(e)


def test_notifier():
    jobs = get_unnotified_jobs()
    check_notify(jobs)


if __name__ == "__main__":
    test_getonboard(criteria)
    test_jsearch(criteria)
    test_notifier()
