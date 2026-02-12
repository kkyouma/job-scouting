from sqlmodel import Session, SQLModel, create_engine, select

from src.config import settings
from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)

# Turso database configuration
# Turso uses libsql protocol which is accessed via HTTP
engine = create_engine(
    f"sqlite+{settings.TURSO_URL}?secure=true",
    echo=False,
    connect_args={
        "auth_token": settings.TURSO_AUTH_TOKEN.get_secret_value(),  # Needed for Turso/libsql
    },
)


def get_session():
    """Generator that yields a database session."""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize the database tables."""
    logger.info("Initializing Turso database...")
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def save_jobs(jobs: list[JobListing]):
    """
    Save jobs to the database.
    Ignores duplicates based on primary key (id).
    """
    if not jobs:
        logger.info("No jobs to save")
        return

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

        try:
            session.commit()
            logger.info(f"✅ Saved {new_jobs} new jobs, skipped {duplicate_jobs} duplicates")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save jobs: {e}")
            raise


def get_unnotified_jobs() -> list[JobListing]:
    """Retrieve jobs that haven't been notified yet."""
    logger.debug("Fetching unnotified jobs from database...")
    with Session(engine) as session:
        statement = select(JobListing).where(JobListing.is_notified == False)  # noqa: E712
        results = session.exec(statement)
        jobs = list(results)
        logger.info(f"Found {len(jobs)} unnotified jobs")
        return jobs


def get_all_jobs() -> list[JobListing]:
    """Retrieve all jobs from the database."""
    logger.debug("Fetching all jobs from database...")
    with Session(engine) as session:
        statement = select(JobListing)
        results = session.exec(statement)
        jobs = list(results)
        logger.info(f"Found {len(jobs)} total jobs")
        return jobs


def mark_jobs_as_notified(job_ids: list[str]):
    """Mark specific jobs as notified."""
    if not job_ids:
        logger.info("No jobs to mark as notified")
        return

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

        try:
            session.commit()
            logger.info(f"✅ Marked {notified_count} jobs as notified, {missing_count} not found")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to mark jobs as notified: {e}")
            raise


def get_job_stats() -> dict[str, int]:
    """Get statistics about jobs in the database."""
    with Session(engine) as session:
        total = session.exec(select(JobListing)).all()
        notified = session.exec(
            select(JobListing).where(JobListing.is_notified == True)  # noqa: E712
        ).all()

        stats = {
            "total_jobs": len(total),
            "notified_jobs": len(notified),
            "unnotified_jobs": len(total) - len(notified),
        }
        logger.info(f"Database stats: {stats}")
        return stats
