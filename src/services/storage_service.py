from sqlmodel import Session, SQLModel, create_engine, select

from src.models import JobListing
from src.util.logger_config import get_logger

# Use a local SQLite database
DATABASE_URL = "sqlite:///jobs.db"

# Create engine (echo=True for debugging if needed, usually False for prod)
engine = create_engine(DATABASE_URL)
logger = get_logger(__name__)


def init_db():
    """Initialize the database tables."""
    logger.info("Initializing database...")
    SQLModel.metadata.create_all(engine)
    logger.debug("Database tables created successfully")


def save_jobs(jobs: list[JobListing]):
    """
    Save jobs to the database.
    Ignores duplicates based on primary key (id).
    """
    logger.info(f"Saving {len(jobs)} jobs to database...")
    new_jobs = 0
    duplicate_jobs = 0

    with Session(engine) as session:
        for job in jobs:
            # Check if exists
            existing = session.get(JobListing, job.id)
            if not existing:
                session.add(job)
                new_jobs += 1
                logger.debug(f"Added new job: {job.title} at {job.company_name}")
            else:
                duplicate_jobs += 1
                logger.debug(f"Skipping duplicate job: {job.title} at {job.company_name}")
        session.commit()

    logger.info(f"Saved {new_jobs} new jobs, skipped {duplicate_jobs} duplicates")


def get_unnotified_jobs() -> list[JobListing]:
    """Retrieve jobs that haven't been notified yet."""
    logger.debug("Fetching unnotified jobs from database...")
    with Session(engine) as session:
        statement = select(JobListing).where(JobListing.is_notified == False)  # noqa: E712 (SQLModel statement)
        results = session.exec(statement)
        jobs = list(results)
        logger.info(f"Found {len(jobs)} unnotified jobs")
        return jobs


def mark_jobs_as_notified(job_ids: list[str]):
    """Mark specific jobs as notified."""
    logger.info(f"Marking {len(job_ids)} jobs as notified...")
    notified_count = 0
    missing_count = 0

    with Session(engine) as session:
        for j_id in job_ids:
            job = session.get(JobListing, j_id)
            if job:
                job.is_notified = True
                session.add(job)
                notified_count += 1
                logger.debug(f"Marked job as notified: {job.title} at {job.company_name}")
            else:
                missing_count += 1
                logger.warning(f"Job not found in database: {j_id}")
        session.commit()

    logger.info(f"Successfully marked {notified_count} jobs as notified, {missing_count} jobs not found")
