import requests

from src.config import settings
from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def search_jobs(self, criteria: SearchCriteria) -> list[JobListing]:
        headers = {
            "X-RapidAPI-Key": settings.JSEARCH_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        query_string = f"{criteria.query}"
        querystring = {
            "query": query_string,
            "page": "1",
            "num_pages": "2",
            "country": criteria.location,
        }

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()

            jobs = []
            if "data" in data:
                for item in data["data"]:
                    jobs.append(
                        JobListing(
                            id=item.get("job_id", ""),
                            title=item.get("job_title", ""),
                            company_name=item.get("employer_name", ""),
                            location=f"{item.get('job_city', '')}, {item.get('job_country', '')}",
                            description=item.get("job_description", "")[:500] + "...",  # Truncate for brevity
                            url=item.get("job_apply_link", ""),
                            source="JSearch",
                            posted_date=None,  # Detailed parsing needed
                            tags=[term for term in [item.get("job_is_remote") and "Remote"] if term],
                        )
                    )
            return jobs
        except Exception as e:
            logger.error(f"Error fetching from JSearch: {e}")
            return []
