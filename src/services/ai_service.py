import json

from google import genai
from pydantic import BaseModel

from src.config import settings
from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class MatchingJobs(BaseModel):
    best_match_ids: list[str]


class AIService:
    """Service to evaluate and filter job listings using Google Gemini."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY.get_secret_value() if settings.GEMINI_API_KEY else None
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.model_id = settings.GEMINI_MODEL_ID

    def evaluate_jobs(self, jobs: list[JobListing]) -> list[JobListing]:
        """
        Evaluate a list of jobs and return the best matches according to Gemini.
        """
        if not self.client:
            logger.warning("GEMINI_API_KEY is not set. Skipping AI evaluation and returning all jobs.")
            return jobs

        if not self.model_id:
            logger.warning("GEMINI_MODEL_ID is not set. Skipping AI evaluation and returning all jobs.")
            return jobs

        if not jobs:
            return []

        logger.info(f"Evaluating {len(jobs)} jobs using {self.model_id}...")
        best_matches = []

        # TODO: Outsource this string to a .md file
        system_prompt = (
            "You are an AI tech recruiter. Your task is to evaluate job descriptions for a "
            "Junior/Mid Data Engineer, Data Scientist, or Data Analyst role.\n"
            "We want to filter out low-quality jobs and keep the ones that mention modern data pipelines, "
            "Python, SQL, cloud, or backend engineering.\n"
            "Identify the IDs of the matching jobs."
        )

        # Batch jobs to avoid exceeding context window length
        batch_size = 20
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            jobs_data = [
                {
                    "id": job.id,
                    "title": job.title,
                    "description": job.description[:2000] if job.description else "",
                    "company": job.company_name,
                }
                for job in batch
            ]

            prompt = f"Here is a batch of jobs: {json.dumps(jobs_data)}"

            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config={
                        "system_instruction": system_prompt,
                        "response_mime_type": "application/json",
                        "response_schema": MatchingJobs,
                    },
                )

                if response.parsed:
                    match_ids = response.parsed.best_match_ids
                    for job in batch:
                        if job.id in match_ids:
                            best_matches.append(job)
                            logger.debug(f"AI selected job: {job.title} at {job.company_name}")
                else:
                    logger.warning("Gemini returned empty or unparseable response.")

            except Exception as e:
                logger.error(f"Error during Gemini evaluation for a batch: {e}")
                # Fallback to including the batch if AI fails to avoid losing jobs
                logger.warning("Adding batch to best matches as fallback due to AI error.")
                best_matches.extend(batch)

        logger.info(f"AI evaluation complete. {len(best_matches)} jobs selected out of {len(jobs)}.")
        return best_matches
