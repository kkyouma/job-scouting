from prefect import flow, task

from src.clients.getonboard import GetOnBoardClient
from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, SearchCriteria
from src.services.filter_service import FilterService
from src.services.notifier import TelegramNotifier
from src.services.storage_service import (
    get_unnotified_jobs,
    init_db,
    mark_jobs_as_notified,
    save_jobs,
)


@task
def fetch_jsearch_jobs(criteria: SearchCriteria) -> list[JobListing]:
    return JSearchClient().search_jobs(criteria, num_pages=2)


@task
def fetch_getonboard_jobs(criteria: SearchCriteria) -> list[JobListing]:
    return GetOnBoardClient().search_jobs(criteria)


@task
def filter_results(jobs: list[JobListing]) -> list[JobListing]:
    return FilterService.filter_jobs(jobs)


@task
def notify_user(jobs: list[JobListing]):
    TelegramNotifier().notify(jobs)


@flow(name="Job Scouting Flow")
def job_flow():
    # 1. Initialize Database
    init_db()

    criteria = SearchCriteria(
        query=settings.DEFAULT_QUERY,
        location=settings.DEFAULT_LOCATION,
        date_posted="today",
    )

    # 2. Fetch Jobs
    # Run fetch tasks in parallel
    jsearch_jobs = fetch_jsearch_jobs(
        criteria
    )  # Using .submit() for parallel if using Dask/Ray, but default runner is sequential/threads.

    getonboard_jobs = fetch_getonboard_jobs(criteria)  #  GetOnBoard might be empty

    all_jobs = jsearch_jobs + getonboard_jobs

    # 3. Filter Jobs (Business Logic)
    filtered_jobs = filter_results(all_jobs)

    # 4. Save to DB (Deduplication happens here)
    save_jobs(filtered_jobs)

    # 5. Get only NEW (unnotified) jobs for notification
    new_jobs_to_notify = get_unnotified_jobs()

    if not new_jobs_to_notify:
        print("No new jobs to notify.")
        return

    # 6. Notify
    notify_user(new_jobs_to_notify)

    # 7. Mark as Notified
    # Extract IDs to mark as notified
    job_ids = [job.id for job in new_jobs_to_notify]
    mark_jobs_as_notified(job_ids)


if __name__ == "__main__":
    job_flow()
