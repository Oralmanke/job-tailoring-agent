from pathlib import Path

from src.matcher import cv_match
from src.db.database import init_db, save_jobs, SessionLocal
from src.scraper.remotive import fetch_remotive
from src.scraper.adzuna import fetch_adzuna
from src.db.models import Job
from src.tailor import tailor_for_job
from src.config import settings
from src.logger import get_logger

log = get_logger(__name__)


def ingest_jobs(
    search: str | None = None,
    country: str | None = None,
    limit: int | None = None,
) -> None:
    """Create tables (if needed) and fetch+store jobs from every source.

    Any source that fails is logged and skipped so one dead API does not block
    ingestion from the others.
    """
    init_db()
    for name, fetch in (("remotive", fetch_remotive), ("adzuna", fetch_adzuna)):
        try:
            save_jobs(fetch(search=search, country=country, limit=limit))
        except Exception as exc:  # noqa: BLE001 - one bad source shouldn't stop the rest
            log.error("Ingestion from %s failed: %s", name, exc)


def tailor_top_matches(cv: Path, n: int = 3) -> None:
    """Match the CV against stored jobs and tailor documents for the top n."""
    cv_md = Path(cv).read_text(encoding="utf-8")
    results = cv_match(cv_md)
    out = Path(settings.output_dir)
    out.mkdir(exist_ok=True)

    with SessionLocal() as session:
        for r in results[:n]:
            job = session.get(Job, r.id)
            try:
                result = tailor_for_job(cv_md, job, out)
                if result is None:
                    log.info("Skipped %s: rejected by checks", job.title)
                else:
                    cv_path_out, cl_path_out = result
                    log.info("OK: %s / %s", cv_path_out.name, cl_path_out.name)
            except Exception as exc:  # noqa: BLE001
                log.error("Failed %s: %s", job.title, exc)
