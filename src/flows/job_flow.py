from prefect import flow, get_run_logger, task

from src.clients.getonboard import GetOnBoardClient
from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, SearchCriteria
from src.services.filter_service import FilterService
from src.services.notifier import TelegramNotifier
from src.services.storage_service import (
    get_unnotified_jobs,
    mark_jobs_as_notified,
    save_jobs,
)


@task(name="Fetch JSearch Jobs", retries=3, retry_delay_seconds=5)
def fetch_jsearch_jobs(criteria: SearchCriteria) -> list[JobListing]:
    logger = get_run_logger()
    jobs = JSearchClient().search_jobs(criteria, num_pages=2)
    logger.info(f"JSearch: found {len(jobs)} jobs.")
    return jobs


@task(name="Fetch GetOnBoard Jobs", retries=3, retry_delay_seconds=5)
def fetch_getonboard_jobs(criteria: SearchCriteria) -> list[JobListing]:
    logger = get_run_logger()
    jobs = GetOnBoardClient().search_jobs(criteria)
    logger.info(f"GetOnBoard: found {len(jobs)} jobs.")
    return jobs


@task(name="Filter Jobs")
def filter_results(jobs: list[JobListing]) -> list[JobListing]:
    logger = get_run_logger()
    logger.info(f"Initial jobs: {len(jobs)}")
    filtered_jobs = FilterService.filter_jobs(jobs)
    logger.info(f"Filtered jobs: {len(filtered_jobs)}")
    return filtered_jobs


@task(name="Notify User", retries=3, retry_delay_seconds=60)
def notify_user(jobs: list[JobListing]):
    logger = get_run_logger()
    logger.info(f"Sending {len(jobs)} notifications")
    return TelegramNotifier().notify(jobs)


@flow(name="Job Scouting Flow")
def job_flow():
    logger = get_run_logger()
    # 1. Initialize Database
    criteria_jsearch = SearchCriteria(
        query="Junior Data Engineer",
        location=settings.DEFAULT_LOCATION,
        date_posted="today",
    )
    criteria_getonboard = SearchCriteria(
        query="Data Engineer",
        location=settings.DEFAULT_LOCATION,
    )

    # 2. Fetch Jobs
    jsearch_jobs = fetch_jsearch_jobs(criteria_jsearch)

    getonboard_jobs = fetch_getonboard_jobs(criteria_getonboard)  #  GetOnBoard might be empty

    all_jobs = getonboard_jobs + jsearch_jobs

    # 3. Filter Jobs (Business Logic)
    filtered_jobs = filter_results(all_jobs)

    # 4. Save to DB (Deduplication happens here)
    save_jobs(filtered_jobs)

    # 5. Get only NEW (unnotified) jobs for notification
    new_jobs_to_notify = get_unnotified_jobs()

    if not new_jobs_to_notify:
        logger.info("No new jobs to notify.")
        return

    # 6. Notify
    notify_user(new_jobs_to_notify)

    # 7. Mark as Notified
    # Extract IDs to mark as notified
    job_ids = [job.id for job in new_jobs_to_notify]
    mark_jobs_as_notified(job_ids)


if __name__ == "__main__":
    job_flow.serve(
        name="daily-job-aggregator",
        cron="0 23 * * *",
        tags=["production"],
    )
