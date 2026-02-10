import sys
from datetime import UTC, datetime

from src.models import JobListing
from src.services.storage_service import get_unnotified_jobs, init_db, mark_jobs_as_notified, save_jobs
from src.util.logger_config import get_logger


def verify():
    logger = get_logger(__name__)
    logger.info("Initializing DB")
    init_db()

    job_id = f"test-id-{int(datetime.now(UTC).timestamp())}"
    job = JobListing(
        id=job_id,
        title="Test Job",
        company_name="Antigravity Inc",
        url="https://example.com/job",
        source="Test",
        tags=["remote", "python"],
    )

    logger.info(f"Saving job {job_id}")
    save_jobs([job])

    logger.info("Checking unnotified jobs")
    pending = get_unnotified_jobs()
    found = False
    for p in pending:
        if p.id == job_id:
            found = True
            logger.info(f"Found job: {p.title} with tags: {p.tags}")
            break

    if not found:
        logger.error("Job not found in pending list!")
        sys.exit(1)

    logger.info("Marking as notified")
    mark_jobs_as_notified([job_id])

    logger.info("Checking pending jobs again (should be empty/ignoring our job)")
    pending_after = get_unnotified_jobs()
    for p in pending_after:
        if p.id == job_id:
            logger.error("Job still in pending list after notification!")
            sys.exit(1)

    logger.info("Storage service verified SUCCESSFULLY!")


if __name__ == "__main__":
    verify()
