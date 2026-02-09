from src.clients.getonboard import GetOnBoardClient
from src.models import SearchCriteria


def main():
    print("Testing GetOnBoard API...")
    # GetOnBoard might not need keys for public search, but good to verify

    criteria = SearchCriteria(query="Python", location="Remote")

    try:
        client = GetOnBoardClient()
        jobs = client.search_jobs(criteria)

        print(f"\nFound {len(jobs)} jobs.")
        for job in jobs[:3]:
            print(f"- {job.title} at {job.company_name} ({job.location})")
            print(f"  URL: {job.url}")
            print("-" * 20)

    except Exception as e:
        print(f"FAILED: {e}")


if __name__ == "__main__":
    main()
