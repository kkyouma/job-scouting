from src.services.storage_service import init_db, save_jobs, get_unnotified_jobs, mark_jobs_as_notified
from src.models import JobListing
from datetime import datetime, UTC
import sys


def verify():
    print("Initializing DB...")
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

    print(f"Saving job {job_id}...")
    save_jobs([job])

    print("Checking unnotified jobs...")
    pending = get_unnotified_jobs()
    found = False
    for p in pending:
        if p.id == job_id:
            found = True
            print(f"Found job: {p.title} with tags: {p.tags}")
            break

    if not found:
        print("ERROR: Job not found in pending list!")
        sys.exit(1)

    print("Marking as notified...")
    mark_jobs_as_notified([job_id])

    print("Checking pending jobs again (should be empty/ignoring our job)...")
    pending_after = get_unnotified_jobs()
    for p in pending_after:
        if p.id == job_id:
            print("ERROR: Job still in pending list after notification!")
            sys.exit(1)

    print("SUCCESS: Storage service verified.")


if __name__ == "__main__":
    verify()
