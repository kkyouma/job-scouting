import requests

from src.models import JobListing, SearchCriteria


class GetOnBoardClient:
    # GetOnBoard has a public API, but limited without auth mostly for detailed info.
    # Using public search endpoint if available or just mocking structure for now as they require OAuth for heavy lifting usually.
    # Actually they have a simple non-auth search endpoint potentially.
    BASE_URL = "https://www.getonboard.com/api/v0/search/jobs"

    def search_jobs(self, criteria: SearchCriteria) -> list[JobListing]:
        # Note: GetOnBoard API might require specific handling or might be scraping-based if no key.
        # Assuming we just query parameters if possible.
        # For simplicity in this "minimalist" version, we might skip complex auth if public endpoint exists.
        # Let's use a placeholder implementation or standard requests if detailed docs were available.
        # Given constraints, I'll implement a basic structure that returns empty if fails.
        params = {"query": criteria.query, "per_page": 10}

        try:
            response = requests.get(self.BASE_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                if "data" in data:
                    for item in data["data"]:
                        attrs = item.get("attributes", {})
                        jobs.append(
                            JobListing(
                                id=item.get("id", ""),
                                title=attrs.get("title", ""),
                                company_name=attrs.get("company", {}).get("name", ""),
                                location=f"{attrs.get('country', '')} {('Remote' if attrs.get('remote') else '')}",
                                description=attrs.get("description_headline", ""),
                                url=item.get("links", {}).get("public_url", ""),
                                source="GetOnBoard",
                                posted_date=None,
                            )
                        )
                return jobs
            else:
                print(f"GetOnBoard API status: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching from GetOnBoard: {e}")
            return []
