import sys
from datetime import UTC, datetime

from src.models import JobListing, JobStage
from src.services.storage_service import get_jobs_by_stage, init_db, mark_jobs_as_notified, promote_jobs, save_jobs
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

    logger.info(f"Saving job {job_id} as RAW")
    save_jobs([job], stage=JobStage.RAW)

    logger.info("Checking RAW jobs")
    raw_jobs = get_jobs_by_stage(JobStage.RAW)
    found = any(p.id == job_id for p in raw_jobs)
    if not found:
        logger.error("Job not found in RAW stage!")
        sys.exit(1)
    logger.info(f"Found job in RAW stage: {job_id}")

    logger.info("Promoting to FILTERED")
    promote_jobs([job_id], new_stage=JobStage.FILTERED)

    logger.info("Promoting to SELECTED")
    promote_jobs([job_id], new_stage=JobStage.SELECTED)

    selected = get_jobs_by_stage(JobStage.SELECTED, notified=False)
    found = any(p.id == job_id for p in selected)
    if not found:
        logger.error("Job not found in SELECTED stage!")
        sys.exit(1)
    logger.info(f"Found job in SELECTED stage: {job_id}")

    logger.info("Marking as notified")
    mark_jobs_as_notified([job_id])

    logger.info("Checking SELECTED+unnotified (should not contain our job)")
    selected_after = get_jobs_by_stage(JobStage.SELECTED, notified=False)
    if any(p.id == job_id for p in selected_after):
        logger.error("Job still unnotified after marking!")
        sys.exit(1)

    logger.info("✅ Storage service verified SUCCESSFULLY!")


if __name__ == "__main__":
    verify()
