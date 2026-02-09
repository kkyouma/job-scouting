from src.models import JobListing, SearchCriteria


class FilterService:
    @staticmethod
    def filter_jobs(
        jobs: list[JobListing], criteria: SearchCriteria
    ) -> list[JobListing]:
        filtered = []
        for job in jobs:
            # Basic filtering logic
            # 1. Deduplication by ID (if we were persisting, but here just filtering the list)
            # 2. Keyword matching in description/title if criteria specified

            # Example: Filter by seniority if specified
            if criteria.seniority:
                content = (job.title + " " + (job.description or "")).lower()
                if criteria.seniority.lower() not in content:
                    continue

            # Example: Filter by experience if specified (harder with text, need parsing)
            # For minimalist MVP, we might skip complex parsing unless regex is added.

            filtered.append(job)

        return filtered
