import json

from google import genai
from google.genai import types
from pydantic import BaseModel

from src.config import settings
from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
You are a technical recruiter assistant filtering job listings for a candidate
seeking a Junior/Mid-level role in Data Engineering, Data Science, or Data Analysis.

A job is RELEVANT if it clearly mentions:
- Python or SQL
- Data pipelines, ETL/ELT, or workflow orchestration (e.g. Airflow, dbt)
- Cloud platforms (AWS, GCP, Azure)
- Machine learning, analytics, or backend data systems

A job is NOT RELEVANT if it is:
- Purely managerial with no hands-on technical work
- Focused on unrelated stacks (e.g. mobile, embedded, frontend only)
- Vague with no technical detail whatsoever

Return ONLY the IDs of the relevant jobs.
""".strip()


class MatchingJobs(BaseModel):
    best_match_ids: list[str]


class AIService:
    """Service to evaluate and filter job listings using Google Gemini."""

    BATCH_SIZE = 20

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.get_secret_value() if settings.GEMINI_API_KEY else None
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model_id = settings.GEMINI_MODEL_ID

    def _serialize_job(self, job: JobListing, max_description_lenght: int = 2000) -> dict:
        return {
            "id": job.id,
            "title": job.title,
            "description": job.description[:max_description_lenght] if job.description else "",
        }

    def _is_ready(self) -> bool:
        if not self.client:
            logger.warning("GEMINI_API_KEY is not set. Skipping AI evaluation and returning all jobs.")
            return False

        if not self.model_id:
            logger.warning("GEMINI_MODEL_ID is not set. Skipping AI evaluation and returning all jobs.")
            return False

        return True

    def _classify_batch(self, batch: list[JobListing]) -> list[str] | None:
        """Send a single batch to Gemini and return the list of matching IDs.

        Returns None if the API call fails.
        """
        jobs_data = [self._serialize_job(job) for job in batch]

        prompt = (
            f"Evaluate the following {len(batch)} job listings and return the IDs of the relevant ones.\n\n"
            f"```json\n{json.dumps(jobs_data, indent=2)}\n```"
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=MatchingJobs,
            ),
        )

        if response.parsed:
            return response.parsed.best_match_ids  # ty:ignore[unresolved-attribute]

        if response.text:
            logger.warning("response.parsed was None — attempting manual JSON parse.")
            data = json.loads(response.text)  # Let this raise if truly malformed
            return MatchingJobs(**data).best_match_ids

        return None

    def evaluate_jobs(self, jobs: list[JobListing]) -> list[JobListing]:
        """
        Evaluate a list of jobs and return the best matches according to Gemini.
        """
        if not self._is_ready():
            return jobs

        if not jobs:
            return []

        logger.info(f"Evaluating {len(jobs)} jobs using {self.model_id}...")
        best_matches: list[JobListing] = []

        batch_size = self.BATCH_SIZE
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            batch_label = i // batch_size + 1

            try:
                match_ids = self._classify_batch(batch)

                if match_ids is None:
                    raise ValueError("Gemini returned an empty response with no pareable content.")

                match_id_set = set(match_ids)
                for job in batch:
                    if job.id in match_id_set:
                        best_matches.append(job)
                        logger.debug(f"AI selected: '{job.title}'")

                logger.info(f"Batch {batch_label}: {len(match_ids)}/{len(batch)} jobs selected.")

            except Exception as e:
                logger.error(f"Batch {batch_label}: Gemini evaluation failed — {e}")
                logger.warning(f"Batch {batch_label}: Falling back to including all {len(batch)} jobs.")
                best_matches.extend(batch)

        logger.info(f"AI evaluation complete. {len(best_matches)}/{len(jobs)} jobs selected.")
        return best_matches
