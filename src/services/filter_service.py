# src/services/filter_service.py
from typing import ClassVar

from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class FilterService:
    TARGET_KEYWORDS: ClassVar[list[str]] = [
        # Seniority
        "junior",
        "jr",
        "trainee",
        "semisenior",
        "semi senior",
        "ssr",
        "early career",
        # Roles
        "data engineer",
        "ingeniero de datos",
        "backend",
        "data scientist",
        "analytics engineer",
        "data analyst",
        "analista de datos",
        "data analytics",
        # Core Stack
        "python",
        "sql",
        "postgresql",
        # Orquestación y ML
        "xgboost",
        "prefect",
        "airflow",
        "dagster",
        # Herramientas Pro
        "dbt",
        "aws",
        "docker",
        "pyspark",
        "pandas",
    ]
    EXCLUDED_KEYWORDS: ClassVar[list[str]] = [
        "senior",
        "sr.",
        "lead",
        "principal",
        "architect",
        "manager",
        "experto",
    ]

    EXCEPTION_KEYWORDS: ClassVar[list[str]] = ["semi senior", "semi-senior", "semisenior"]

    @staticmethod
    def filter_jobs(jobs: list[JobListing]) -> list[JobListing]:
        filtered = []
        logger.info(f"Filtrando {len(jobs)} ofertas...")

        for job in jobs:
            text_content = (f"{job.title} {job.description or ''} {job.company_name}").lower()

            is_excluded = False
            for bad_word in FilterService.EXCLUDED_KEYWORDS:
                if bad_word in text_content:
                    is_safe_exception = any(exc in text_content for exc in FilterService.EXCEPTION_KEYWORDS)

                    if not is_safe_exception:
                        is_excluded = True
                        break

            if is_excluded:
                continue

            if not FilterService.TARGET_KEYWORDS:
                filtered.append(job)
                continue

            if any(target in text_content for target in FilterService.TARGET_KEYWORDS):
                filtered.append(job)

        logger.info(f"Filtro completado: {len(filtered)} ofertas seleccionadas de {len(jobs)}.")
        return filtered
