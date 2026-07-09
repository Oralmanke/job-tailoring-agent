from datetime import datetime

from pydantic import BaseModel


class JobOut(BaseModel):
    """Public shape of a job row returned by the API."""

    id: int
    title: str | None = None
    company: str | None = None
    location: str | None = None
    url: str | None = None
    source: str | None = None
    created: datetime | None = None

    model_config = {"from_attributes": True}


class TailorAccepted(BaseModel):
    """Returned when a tailoring job is queued as a background task."""

    job_id: int
    status: str


class TailorStatus(BaseModel):
    """Current state of a tailoring job."""

    job_id: int
    status: str
    error: str | None = None
    cv: str | None = None
    cover_letter: str | None = None
