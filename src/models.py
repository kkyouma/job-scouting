from datetime import UTC, datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class JobListing(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    company_name: str
    seniority: str | None = None
    location: str | None = None
    modality: str | None = None
    description: str | None = None
    url: str
    salary: int | None = None
    posted_date: datetime | None = None
    source: str  # e.g., "JSearch", "Adzuna", "GetOnBoard"
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Tracking fields
    is_notified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SearchCriteria(SQLModel):
    query: str
    location: str | None = None
    min_salary: float | None = None
    seniority: str | None = None
    experience_years: int | None = None
    date_posted: datetime | str | None = None
