# src/services/filter_service.py
from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class FilterService:
    # 1. Palabras que SÍ o SÍ queremos (si la lista está vacía, trae todo lo que no esté excluido)
    TARGET_KEYWORDS = [
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
    # 2. Palabras que NO queremos bajo ningún concepto
    EXCLUDED_KEYWORDS = [
        "senior",
        "sr.",
        "lead",
        "principal",
        "architect",
        "manager",
        "experto",
    ]

    # 3. Excepciones: Si aparece una palabra excluida (ej: "Senior"),
    # pero está dentro de esta frase (ej: "Semi Senior"), la perdonamos.
    EXCEPTION_KEYWORDS = ["semi senior", "semi-senior", "semisenior"]

    @staticmethod
    def filter_jobs(jobs: list[JobListing]) -> list[JobListing]:
        filtered = []
        logger.info(f"Filtrando {len(jobs)} ofertas...")

        for job in jobs:
            # Normalizamos todo el texto relevante a minúsculas para buscar fácil
            text_content = (f"{job.title} {job.description or ''} {job.company_name}").lower()

            # --- PASO A: Verificar Exclusiones ---
            is_excluded = False
            for bad_word in FilterService.EXCLUDED_KEYWORDS:
                if bad_word in text_content:
                    # ¡ALERTA! Encontramos una palabra prohibida.
                    # Pero antes de descartar, chequeamos si es una excepción (ej: "Semi Senior")
                    is_safe_exception = any(exc in text_content for exc in FilterService.EXCEPTION_KEYWORDS)

                    if not is_safe_exception:
                        is_excluded = True
                        break  # Ya está excluida, no busques más

            if is_excluded:
                continue  # Saltamos a la siguiente oferta

            # --- PASO B: Verificar Inclusiones (Match) ---
            # Si no definiste keywords objetivo, asumimos que quieres todo lo que pasó el filtro de exclusión.
            if not FilterService.TARGET_KEYWORDS:
                filtered.append(job)
                continue

            # Si definiste keywords, al menos una debe estar presente
            if any(target in text_content for target in FilterService.TARGET_KEYWORDS):
                filtered.append(job)

        logger.info(f"Filtro completado: {len(filtered)} ofertas seleccionadas de {len(jobs)}.")
        return filtered
