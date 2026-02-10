from src.models import JobListing, SearchCriteria


class FilterService:
    @staticmethod
    def filter_jobs(jobs: list[JobListing], criteria: SearchCriteria) -> list[JobListing]:
        filtered = []
        for job in jobs:
            # 1. Keyword matching
            # We look for keywords in the 'query' or purely rely on title/description match
            # if the user adds specific 'keywords' to criteria later we can use that.
            # For now, we'll assume the basic criteria application.

            # Combine text for easier searching
            text_content = (f"{job.title} {job.description or ''} {job.company_name}").lower()

            # Example: Filter by seniority if specified
            if criteria.seniority and criteria.seniority.lower() not in text_content:
                continue

            # Example: Filter by min_salary (if parsable)
            # This is complex without a standardized salary field, skipping for minimalist MVP

            # Example: Explicit negative keywords (could be added to config)
            # if "scam" in text_content: continue

            filtered.append(job)

        return filtered
