"""In-memory tracking + background execution of tailoring jobs.

The store is a simple process-local dict — intentionally lightweight. For a
single-instance deployment it is enough to report progress and locate output
files; a multi-worker setup would swap this for a table or Redis.
"""
from pathlib import Path
from threading import Lock

from src.config import settings
from src.convert import to_markdown
from src.db.database import SessionLocal
from src.db.models import Job
from src.logger import get_logger
from src.tailor import tailor_for_job

log = get_logger(__name__)

# job_id -> {status, cv, cover_letter, error}
_STATUS: dict[int, dict] = {}
_lock = Lock()

PENDING, RUNNING, DONE, FAILED, NOT_FOUND = (
    "pending", "running", "done", "failed", "not_found",
)


def _set(job_id: int, **fields) -> None:
    with _lock:
        _STATUS.setdefault(job_id, {}).update(fields)


def get_status(job_id: int) -> dict:
    """Return the current tracked status for a job, or a not_found placeholder."""
    with _lock:
        return dict(_STATUS.get(job_id, {"status": NOT_FOUND}))


def mark_pending(job_id: int) -> None:
    _set(job_id, status=PENDING, cv=None, cover_letter=None, error=None)


def _load_cv_markdown() -> str:
    """Load the default CV and convert it to markdown for the prompts."""
    return Path(to_markdown(Path(settings.default_cv_path))).read_text(encoding="utf-8")


def run_tailoring(job_id: int) -> None:
    """Background worker: tailor the CV + cover letter for one job id."""
    _set(job_id, status=RUNNING)
    try:
        cv_md = _load_cv_markdown()
        out = Path(settings.output_dir)
        out.mkdir(exist_ok=True)

        with SessionLocal() as session:
            job = session.get(Job, job_id)
            if job is None:
                _set(job_id, status=FAILED, error="job not found")
                return
            result = tailor_for_job(cv_md, job, out)

        if result is None:
            _set(job_id, status=FAILED, error="rejected by quality checks")
        else:
            cv_path, cl_path = result
            _set(job_id, status=DONE, cv=str(cv_path), cover_letter=str(cl_path))
            log.info("Tailoring done for job %s", job_id)
    except Exception as exc:  # noqa: BLE001 - report any failure to the caller
        log.error("Tailoring failed for job %s: %s", job_id, exc)
        _set(job_id, status=FAILED, error=str(exc))
