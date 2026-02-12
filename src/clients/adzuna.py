import json

import requests

from src.config import settings
from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger
from src.util.normalizer import extract_modality_from_text, extract_seniority_from_title

logger = get_logger(__name__)


class AdzunaClient:
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"  # Defaulting to US, can be configurable

    def _calculate_salary(
        self,
        min_salary: int | None,
        max_salary: int | None,
    ) -> int:
        if min_salary is not None and max_salary is not None:
            return int((min_salary + max_salary) / 2)
        elif min_salary is not None:
            return int(min_salary)
        elif max_salary is not None:
            return int(max_salary)
        else:
            return 0

    def search_jobs(
        self, criteria: SearchCriteria, filter_recent: bool = True, recent_days: int = 2
    ) -> list[JobListing]:
        params = {
            "app_id": settings.ADZUNA_APP_ID,
            "app_key": settings.ADZUNA_API_KEY.get_secret_value(),
            "results_per_page": 20,
            "what": criteria.query,
            "where": criteria.location,
            "content-type": "application/json",
            "max_days_old": recent_days if filter_recent else None,
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            with open("adzuna.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            jobs = []
            if "results" in data:
                for item in data["results"]:
                    # Filter by date if enabled
                    created_date = item.get("created")
                    title = item.get("title", "")
                    description = item.get("description", "")

                    # Extract seniority from title
                    seniority = extract_seniority_from_title(title)

                    # Extract modality from title and description
                    modality = extract_modality_from_text(f"{title} {description}")

                    jobs.append(
                        JobListing(
                            id=str(item.get("id", "")),
                            title=title,
                            company_name=item.get("company", {}).get("display_name", ""),
                            location=", ".join(item.get("location", {}).get("area", [])),
                            description=description,
                            url=item.get("redirect_url", ""),
                            salary=self._calculate_salary(item.get("salary_min"), item.get("salary_max")),
                            source="Adzuna",
                            posted_date=created_date,
                            seniority=seniority,
                            modality=modality,
                        )
                    )
            logger.info(jobs)
            return jobs
        except requests.exceptions.HTTPError as e:
            logger.error(f"Adzuna API HTTP error: {e} | Response: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching from Adzuna: {e}")
            return []
