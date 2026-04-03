from sqlmodel import Session, SQLModel, create_engine, select

from src.config import settings
from src.models import JobListing, JobStage
from src.util.logger_config import get_logger

logger = get_logger(__name__)

# Turso database configuration
_turso_host = settings.TURSO_URL.replace("libsql://", "", 1)
engine = create_engine(
    f"sqlite+libsql://{_turso_host}?secure=true",
    echo=False,
    connect_args={
        "auth_token": settings.TURSO_AUTH_TOKEN.get_secret_value(),
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


def save_jobs(jobs: list[JobListing], stage: JobStage = JobStage.RAW):
    """
    Save jobs to the database with a given stage.
    Ignores duplicates based on primary key (id).
    """
    if not jobs:
        logger.info("No jobs to save")
        return

    logger.info(f"Saving {len(jobs)} jobs (stage={stage})...")
    new_count = 0
    duplicate_count = 0

    with Session(engine, expire_on_commit=False) as session:
        for job in jobs:
            existing = session.get(JobListing, job.id)
            if not existing:
                job.stage = stage
                session.add(job)
                new_count += 1
            else:
                duplicate_count += 1

        try:
            session.commit()
            logger.info(f"Saved {new_count} new jobs, skipped {duplicate_count} duplicates")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save jobs: {e}")
            raise


def get_jobs_by_stage(stage: JobStage, notified: bool | None = None) -> list[JobListing]:
    """
    Query jobs by pipeline stage.
    Optionally filter by notification status.
    """
    with Session(engine, expire_on_commit=False) as session:
        statement = select(JobListing).where(JobListing.stage == stage)

        if notified is not None:
            statement = statement.where(JobListing.is_notified == notified)

        results = session.exec(statement)
        jobs = list(results)
        suffix = f" (notified={notified})" if notified is not None else ""
        logger.info(f"Found {len(jobs)} jobs at stage={stage}{suffix}")
        return jobs


def promote_jobs(job_ids: list[str], new_stage: JobStage):
    """
    Move jobs to the next pipeline stage.
    """
    if not job_ids:
        logger.info("No jobs to promote")
        return

    logger.info(f"Promoting {len(job_ids)} jobs → {new_stage}...")
    promoted = 0

    with Session(engine) as session:
        for j_id in job_ids:
            job = session.get(JobListing, j_id)
            if job:
                job.stage = new_stage
                session.add(job)
                promoted += 1
            else:
                logger.warning(f"Job not found for promotion: {j_id}")

        try:
            session.commit()
            logger.info(f"Promoted {promoted} jobs to {new_stage}")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to promote jobs: {e}")
            raise


def mark_jobs_as_notified(job_ids: list[str]):
    """Mark specific jobs as notified."""
    if not job_ids:
        logger.info("No jobs to mark as notified")
        return

    logger.info(f"Marking {len(job_ids)} jobs as notified...")
    notified_count = 0

    with Session(engine) as session:
        for j_id in job_ids:
            job = session.get(JobListing, j_id)
            if job:
                job.is_notified = True
                session.add(job)
                notified_count += 1
            else:
                logger.warning(f"Job not found in database: {j_id}")

        try:
            session.commit()
            logger.info(f"Marked {notified_count} jobs as notified")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to mark jobs as notified: {e}")
            raise


def get_job_stats() -> dict[str, int]:
    """Get statistics about jobs in the database, grouped by stage."""
    with Session(engine) as session:
        all_jobs = session.exec(select(JobListing)).all()

        stats = {
            "total": len(all_jobs),
            "raw": sum(1 for j in all_jobs if j.stage == JobStage.RAW),
            "filtered": sum(1 for j in all_jobs if j.stage == JobStage.FILTERED),
            "selected": sum(1 for j in all_jobs if j.stage == JobStage.SELECTED),
            "notified": sum(1 for j in all_jobs if j.is_notified),
        }
        logger.info(f"Database stats: {stats}")
        return stats
