"""CLI entrypoint: ingest jobs, embed them, then tailor the top matches.

Run with ``python -m src.main``. The HTTP API lives in ``src.api.app`` and is
started separately with uvicorn.
"""
from pathlib import Path

from src.config import settings
from src.convert import to_markdown
from src.matcher import embed_jobs
from src.pipeline import ingest_jobs, tailor_top_matches


def main() -> None:
    ingest_jobs()
    embed_jobs()
    cv_md = to_markdown(Path(settings.default_cv_path))
    tailor_top_matches(cv_md, n=3)


if __name__ == "__main__":
    main()
