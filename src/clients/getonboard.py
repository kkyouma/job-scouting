import json

import requests

from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger

logger = get_logger(__name__, 10)


class GetOnBoardClient:
    BASE_URL = "https://www.getonbrd.com/api/v0/search/jobs"

    def search_jobs(self, criteria: SearchCriteria) -> list[JobListing]:
        params = {"query": criteria.query, "per_page": 10, "country_code": "CL"}

        try:
            response = requests.request("GET", url=self.BASE_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                jobs = []
                if "data" in data:
                    for item in data["data"]:
                        logger.debug(json.dumps(item, indent=4))

                        attrs = item.get("attributes", {})
                        jobs.append(
                            JobListing(
                                id=item.get("id", ""),
                                title=attrs.get("title", ""),
                                company_name=attrs.get("company", {})
                                .get("data", "")
                                .get("attributes", {})
                                .get("name", ""),
                                location=f"{attrs.get('country', '')}{(' Remote' if attrs.get('remote') else '')}",
                                description=attrs.get("description_headline", ""),
                                url=item.get("links", {}).get("public_url", ""),
                                source="GetOnBoard",
                                posted_date=None,
                                seniority=item.get("seniority", ""),
                            )
                        )
                return jobs
            else:
                logger.warning(f"GetOnBoard API status: {response.status_code}")
                return []
        except Exception as e:
            logger.exception(f"Error fetching from GetOnBoard: {e}")
            return []
