from prefect import flow, task

from src.clients.adzuna import AdzunaClient
from src.clients.getonboard import GetOnBoardClient
from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, SearchCriteria
from src.services.filter_service import FilterService
from src.services.notifier import TelegramNotifier


@task
def fetch_jsearch_jobs(criteria: SearchCriteria) -> list[JobListing]:
    return JSearchClient().search_jobs(criteria)


@task
def fetch_adzuna_jobs(criteria: SearchCriteria) -> list[JobListing]:
    return AdzunaClient().search_jobs(criteria)


@task
def fetch_getonboard_jobs(criteria: SearchCriteria) -> list[JobListing]:
    return GetOnBoardClient().search_jobs(criteria)


@task
def filter_results(
    jobs: list[JobListing], criteria: SearchCriteria
) -> list[JobListing]:
    return FilterService.filter_jobs(jobs, criteria)


@task
def notify_user(jobs: list[JobListing]):
    TelegramNotifier().notify(jobs)


@flow(name="Job Scouting Flow")
def job_scouting_flow():
    criteria = SearchCriteria(
        query=settings.DEFAULT_QUERY,
        location=settings.DEFAULT_LOCATION,
        seniority="Senior",  # Example hardcoded for now, or could come from env/params
    )

    # Run fetch tasks in parallel
    jsearch_jobs = fetch_jsearch_jobs(
        criteria
    )  # Using .submit() for parallel if using Dask/Ray, but default runner is sequential/threads.
    # Actually Prefect 3/future runs tasks concurrently by default if async, but these are sync.
    # To run parallel in sync, we might just let Prefect handle it or use submit.
    # For simplicity, sequential is fine for MVP or use standard execution.

    adzuna_jobs = fetch_adzuna_jobs(criteria)
    getonboard_jobs = fetch_getonboard_jobs(criteria)  #  GetOnBoard might be empty

    all_jobs = jsearch_jobs + adzuna_jobs + getonboard_jobs

    filtered_jobs = filter_results(all_jobs, criteria)

    notify_user(filtered_jobs)


if __name__ == "__main__":
    job_scouting_flow()
