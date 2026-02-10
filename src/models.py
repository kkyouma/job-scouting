from datetime import datetime

from pydantic import BaseModel, Field


class JobListing(BaseModel):
    id: str
    title: str
    company_name: str
    location: str | None = None
    description: str | None = None
    url: str
    salary: str | None = None
    posted_date: datetime | None = None
    source: str  # e.g., "JSearch", "Adzuna", "GetOnBoard"
    tags: list[str] = Field(default_factory=list)


class SearchCriteria(BaseModel):
    query: str
    location: str | None = None
    min_salary: float | None = None
    seniority: str | None = None  # e.g., "Junior", "Senior"
    experience_years: int | None = None
    date_posted: datetime | str | None = None
