import json

import requests

from src.models import JobListing, SearchCriteria
from src.util.logger_config import get_logger
from src.util.normalizer import normalize_location, normalize_modality, normalize_seniority

logger = get_logger(__name__)


class GetOnBoardClient:
    BASE_URL = "https://www.getonbrd.com/api/v0/search/jobs"

    def _calculate_salary(self, attrs: dict) -> str:
        min_salary = attrs.get("min_salary")
        max_salary = attrs.get("max_salary")

        if min_salary is not None and max_salary is not None:
            return str(int((min_salary + max_salary) / 2))
        elif min_salary is not None:
            return str(int(min_salary))
        elif max_salary is not None:
            return str(int(max_salary))
        else:
            return "No especificado"

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

                        # attributes
                        seniority_id = attrs.get("seniority", {}).get("data", {}).get("id")
                        jobs.append(
                            JobListing(
                                id=item.get("id", ""),
                                title=attrs.get("title", ""),
                                company_name=attrs.get("company", {})
                                .get("data", "")
                                .get("attributes", {})
                                .get("name", ""),
                                location=normalize_location(attrs.get("countries", "")),
                                description=f"Descripcion: {attrs.get('description', 'No especificado')}\n"
                                f"Funciones: {attrs.get('functions', 'No especificado')}\n"
                                f"Deseable: {attrs.get('desirable', 'No especificado')}",
                                url=item.get("links", {}).get("public_url", ""),
                                source="GetOnBoard",
                                posted_date=None,
                                seniority=normalize_seniority(seniority_id),
                                modality=normalize_modality(attrs.get("remote_modality", "")),
                                salary=self._calculate_salary(attrs),
                            )
                        )
                return jobs
            else:
                logger.warning(f"GetOnBoard API status: {response.status_code}")
                return []
        except Exception as e:
            logger.exception(f"Error fetching from GetOnBoard: {e}")
            return []
