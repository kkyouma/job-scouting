from sqlmodel import SQLModel, Session, create_engine, select
from src.models import JobListing

# Use a local SQLite database
DATABASE_URL = "sqlite:///jobs.db"

# Create engine (echo=True for debugging if needed, usually False for prod)
engine = create_engine(DATABASE_URL)


def init_db():
    """Initialize the database tables."""
    SQLModel.metadata.create_all(engine)


def save_jobs(jobs: list[JobListing]):
    """
    Save jobs to the database.
    Ignores duplicates based on primary key (id).
    """
    with Session(engine) as session:
        for job in jobs:
            # Check if exists
            existing = session.get(JobListing, job.id)
            if not existing:
                session.add(job)
            else:
                # Optional: Update existing job if needed (e.g. updated fields)
                # For now, we assume first seen is good enough, or we merge.
                pass
        session.commit()


def get_unnotified_jobs() -> list[JobListing]:
    """Retrieve jobs that haven't been notified yet."""
    with Session(engine) as session:
        statement = select(JobListing).where(JobListing.is_notified == False)
        results = session.exec(statement)
        return list(results)


def mark_jobs_as_notified(job_ids: list[str]):
    """Mark specific jobs as notified."""
    with Session(engine) as session:
        for j_id in job_ids:
            job = session.get(JobListing, j_id)
            if job:
                job.is_notified = True
                session.add(job)
        session.commit()
