from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.api import tasks
from src.api.deps import get_db
from src.api.schemas import JobOut, TailorAccepted, TailorStatus
from src.db.models import Job
from src.export import to_pdf
from src.logger import get_logger
from src.matcher import embed_jobs
from src.pipeline import ingest_jobs

log = get_logger(__name__)

app = FastAPI(
    title="Job Tailoring Agent",
    description="Match a CV against scraped jobs and generate tailored CVs "
                "and cover letters.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    """Liveness probe used by Docker healthchecks."""
    return {"status": "ok"}


def _ingest_and_embed(search: str | None, country: str | None, limit: int | None) -> None:
    """Background worker: fetch jobs for the given search, then embed them."""
    ingest_jobs(search=search, country=country, limit=limit)
    embed_jobs()


@app.post("/ingest", status_code=202)
def ingest(
    background_tasks: BackgroundTasks,
    search: str | None = Query(None, description="What to search for, e.g. 'python backend'"),
    country: str | None = Query(None, description="Adzuna country code, e.g. 'de', 'uk'"),
    limit: int | None = Query(None, ge=1, le=100, description="Max results per source"),
) -> dict:
    """Fetch jobs from the sources for a user-chosen search term (runs in background).

    This is how jobs get INTO the database. The search word is no longer baked
    into config only — the caller can pass it here. Omitted params fall back to
    the config defaults.
    """
    background_tasks.add_task(_ingest_and_embed, search, country, limit)
    return {
        "status": "accepted",
        "search": search or "(config default)",
        "country": country or "(config default)",
    }


@app.get("/jobs", response_model=list[JobOut])
def list_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source: str | None = Query(None, description="Filter by 'adzuna' or 'remotive'"),
    location: str | None = Query(None, description="City/country substring, e.g. 'Berlin'"),
    remote: bool | None = Query(None, description="true = only remote jobs"),
    db: Session = Depends(get_db),
) -> list[Job]:
    """List stored jobs, most recent first, with optional filters.

    - ``source``   exact source name
    - ``location`` case-insensitive substring match on the job's location
    - ``remote``   when true, keep only jobs that mention "remote" in the
      location or description
    """
    query = db.query(Job)
    if source:
        query = query.filter(Job.source == source)
    if location:
        # ilike = case-insensitive LIKE; %...% = "contains".
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if remote:
        # Remotive is a remote-only board, so every job from it counts as remote
        # even when its location text says "Worldwide"/"USA"/"Europe" instead of
        # the literal word "remote". We also catch remote wording from any source.
        query = query.filter(
            or_(
                Job.source == "remotive",
                Job.location.ilike("%remote%"),
                Job.location.ilike("%worldwide%"),
                Job.location.ilike("%anywhere%"),
                Job.description.ilike("%remote%"),
            )
        )
    return query.order_by(Job.created.desc().nullslast()).offset(offset).limit(limit).all()


@app.post("/tailor/{job_id}", response_model=TailorAccepted, status_code=202)
def tailor_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> TailorAccepted:
    """Queue tailoring for one job and return immediately (202 Accepted).

    Poll ``GET /tailor/{job_id}/status`` to follow progress.
    """
    if db.get(Job, job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")

    tasks.mark_pending(job_id)
    background_tasks.add_task(tasks.run_tailoring, job_id)
    return TailorAccepted(job_id=job_id, status=tasks.PENDING)


@app.get("/tailor/{job_id}/status", response_model=TailorStatus)
def tailor_status(job_id: int) -> TailorStatus:
    """Return the current status of a queued/running/finished tailoring job."""
    status = tasks.get_status(job_id)
    return TailorStatus(job_id=job_id, **status)


@app.get("/download/{job_id}")
def download(
    job_id: int,
    format: str = Query("docx", pattern="^(docx|pdf)$"),
    doc: str = Query("cv", pattern="^(cv|cover_letter)$"),
) -> FileResponse:
    """Download a generated document for a job.

    ``doc`` selects the CV or the cover letter; ``format`` picks docx (as
    generated) or pdf (converted on the fly via LibreOffice).
    """
    status = tasks.get_status(job_id)
    if status.get("status") != tasks.DONE:
        raise HTTPException(
            status_code=409,
            detail=f"No finished document for job {job_id} "
                   f"(status: {status.get('status')})",
        )

    docx_path = status.get(doc)
    if not docx_path or not Path(docx_path).exists():
        raise HTTPException(status_code=404, detail=f"{doc} file not available")

    path = Path(docx_path)
    if format == "pdf":
        try:
            path = to_pdf(path)
        except (RuntimeError, OSError) as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc

    return FileResponse(path, filename=path.name)
