from prefect import flow, get_run_logger, task

from src.clients.getonboard import GetOnBoardClient
from src.clients.jsearch import JSearchClient
from src.config import settings
from src.models import JobListing, JobStage, SearchCriteria
from src.services.filter_service import FilterService
from src.services.notifier import TelegramNotifier
from src.services.storage_service import (
    get_jobs_by_stage,
    mark_jobs_as_notified,
    promote_jobs,
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


@task(name="Evaluate Jobs with AI", retries=2, retry_delay_seconds=10)
def evaluate_jobs_with_ai(jobs: list[JobListing]) -> list[JobListing]:
    logger = get_run_logger()
    logger.info(f"Passed {len(jobs)} jobs to AI evaluation.")
    from src.services.ai_service import AIService

    ai_service = AIService()
    best_matches = ai_service.evaluate_jobs(jobs)
    logger.info(f"AI Selected {len(best_matches)} best matches.")
    return best_matches


@flow(name="Job Scouting Flow", timeout_seconds=300)
def job_flow():
    logger = get_run_logger()

    # GetOnBoard
    getonboard_queries = [
        "Analytics Engineer",
        "Data Engineer",
        "Data Analyst",
        "ML Engineer",
    ]

    getonboard_futures = [
        fetch_getonboard_jobs.submit(SearchCriteria(query=q, location=settings.DEFAULT_LOCATION))
        for q in getonboard_queries
    ]

    # JSearch
    criteria_jsearch = SearchCriteria(
        query="Analytics Engineer OR Data Engineer",
        location=settings.DEFAULT_LOCATION,
        date_posted="today",
    )

    # 1. Fetch → Save as RAW
    jsearch_future = fetch_jsearch_jobs.submit(criteria_jsearch)
    jsearch_jobs = jsearch_future.result()

    getonboard_jobs = [job for f in getonboard_futures for job in f.result()]

    all_jobs = getonboard_jobs + jsearch_jobs
    save_jobs(all_jobs, stage=JobStage.RAW)

    # 2. Filter → Promote to FILTERED
    filtered_jobs = filter_results(all_jobs)
    if not filtered_jobs:
        logger.info("No jobs passed the keyword filter.")
        return

    filtered_ids = [job.id for job in filtered_jobs]
    promote_jobs(filtered_ids, new_stage=JobStage.FILTERED)

    # 3. AI Evaluation → Promote to SELECTED
    best_matches = evaluate_jobs_with_ai(filtered_jobs)
    if not best_matches:
        logger.info("No best matches found by AI.")
        return

    selected_ids = [job.id for job in best_matches]
    promote_jobs(selected_ids, new_stage=JobStage.SELECTED)

    # 4. Notify only NEW selected jobs (not yet notified)
    jobs_to_notify = get_jobs_by_stage(JobStage.SELECTED, notified=False)
    if not jobs_to_notify:
        logger.info("No new selected jobs to notify.")
        return

    notify_user(jobs_to_notify)

    # 5. Mark as notified
    notified_ids = [job.id for job in jobs_to_notify]
    mark_jobs_as_notified(notified_ids)


if __name__ == "__main__":
    job_flow()
