import requests

from src.config import settings
from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger
from src.util.normalizer import extract_modality_from_text, extract_seniority_from_title, normalize_location

logger = get_logger(__name__)


class JSearchClient:
    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def search_jobs(
        self,
        criteria: SearchCriteria,
        page: int = 1,
        num_pages: int = 1,
    ) -> list[JobListing]:
        headers = {
            "X-RapidAPI-Key": settings.JSEARCH_API_KEY.get_secret_value(),
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }

        querystring = {
            "query": criteria.query,
            "page": str(page),
            "num_pages": str(num_pages),
            "country": criteria.location,
            "date_posted": criteria.date_posted,
        }

        try:
            response = requests.get(self.BASE_URL, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()

            jobs = []
            if "data" in data:
                for item in data["data"]:
                    # Filter by date if enabled
                    title = item.get("job_title", "")
                    description = item.get("job_description", "")

                    # Extract seniority from title
                    seniority = extract_seniority_from_title(title)

                    # Extract modality from title, description, and job_is_remote flag
                    if item.get("job_is_remote"):
                        modality = "Remote"
                    else:
                        modality = extract_modality_from_text(f"{title} {description}")

                    jobs.append(
                        JobListing(
                            id=item.get("job_id", ""),
                            title=title,
                            company_name=item.get("employer_name", ""),
                            location=normalize_location(item.get("job_country", "")),
                            description=description,
                            url=item.get("job_apply_link", ""),
                            source=item.get("job_publisher", "JSearch"),
                            posted_date=item.get("job_posted_at_datetime_utc", ""),
                            seniority=seniority,
                            modality=modality,
                        )
                    )
            return jobs
        except Exception as e:
            logger.error(f"Error fetching from JSearch: {e}")
            return []
