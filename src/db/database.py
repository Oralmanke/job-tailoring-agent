from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import base
from src.config import settings
from sqlalchemy.dialects.postgresql import insert
from .models import Job
from src.logger import get_logger

log = get_logger(__name__)

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Ensure the pgvector extension and all tables exist."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    base.metadata.create_all(engine)


def save_jobs(jobs: list[dict]) -> None:
    """Insert jobs, skipping any whose url already exists (dedup on url)."""
    if not jobs:
        return
    with SessionLocal() as session:
        for job in jobs:
            stmt = (
                insert(Job).values(**job).on_conflict_do_nothing(index_elements=["url"])
            )
            session.execute(stmt)
        session.commit()
    log.info("Saved up to %s jobs", len(jobs))