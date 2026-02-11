import json

import requests

from src.config import settings
from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def search_jobs(self, criteria: SearchCriteria, page: int = 1, num_pages: int = 1) -> list[JobListing]:
        headers = {
            "X-RapidAPI-Key": settings.JSEARCH_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        querystring = {
            "query": criteria.query,
            "page": str(page),
            "num_pages": str(num_pages),
            "country": criteria.location,
        }

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            with open("respuesta.json", "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=4)

            jobs = []
            if "data" in data:
                for item in data["data"]:
                    jobs.append(
                        JobListing(
                            id=item.get("job_id", ""),
                            title=item.get("job_title", ""),
                            company_name=item.get("employer_name", ""),
                            location=f"{item.get('job_city', '')}, {item.get('job_country', '')}",
                            description=item.get("job_description", ""),
                            url=item.get("job_apply_link", ""),
                            source=item.get("job_publisher", ""),
                            posted_date=item.get("job_posted_at_datetime_utc", ""),  # Detailed parsing needed
                            tags=[term for term in [item.get("job_is_remote") and "Remote"] if term],
                        )
                    )
            return jobs
        except Exception as e:
            logger.error(f"Error fetching from JSearch: {e}")
            return []
