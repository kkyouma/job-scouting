from src.clients.jsearch import JSearchClient
from src.models import SearchCriteria
from src.config import settings

def main():
    print("Testing JSearch API...")
    if not settings.JSEARCH_API_KEY.get_secret_value() or "your_" in settings.JSEARCH_API_KEY.get_secret_value():
        print("WARNING: JSEARCH_API_KEY seems to be default or empty. Please check your .env file.")

    criteria = SearchCriteria(
        query="Python Developer",
        location="Remote"
    )
    
    try:
        client = JSearchClient()
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
