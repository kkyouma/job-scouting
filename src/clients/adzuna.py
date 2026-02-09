import requests

from src.config import settings
from src.models import JobListing, SearchCriteria


class AdzunaClient:
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"  # Defaulting to US, can be configurable

    def search_jobs(self, criteria: SearchCriteria) -> list[JobListing]:
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY.get_secret_value(),
            "results_per_page": 20,
            "what": criteria.query,
            "where": criteria.location,
            "content-type": "application/json",
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            jobs = []
            if "results" in data:
                for item in data["results"]:
                    jobs.append(
                        JobListing(
                            id=str(item.get("id", "")),
                            title=item.get("title", ""),
                            company_name=item.get("company", {}).get(
                                "display_name", ""
                            ),
                            location=", ".join(
                                item.get("location", {}).get("area", [])
                            ),
                            description=item.get("description", "")[:500] + "...",
                            url=item.get("redirect_url", ""),
                            salary=f"{item.get('salary_min')} - {item.get('salary_max')}"
                            if item.get("salary_min")
                            else None,
                            source="Adzuna",
                            posted_date=None,  # timestamp usually
                        )
                    )
            return jobs
        except Exception as e:
            print(f"Error fetching from Adzuna: {e}")
            return []
