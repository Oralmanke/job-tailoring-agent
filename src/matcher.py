from src.db.database import SessionLocal
from src.embedding import embed
from src.db.models import Job
from sqlalchemy import select
from src.logger import get_logger

log = get_logger(__name__)


def embed_jobs() -> None:
    """Compute and store embeddings for every job that doesn't have one yet."""
    texts = []
    with SessionLocal() as session:
        jobs_without_embed = session.query(Job).filter(Job.embedding.is_(None)).all()
        if not jobs_without_embed:
            log.info("All jobs already embedded")
            return
        for job in jobs_without_embed:
            text = f"{job.title}. {job.description}"
            texts.append(text)
        
        for vec, job in zip(embed(texts),jobs_without_embed):
            job.embedding = vec
        session.commit()


def cv_match(cv_text: str, top_k: int = 50):
    """Return the top_k jobs most similar to the CV, ordered by cosine score.

    Each row exposes (id, title, company, score) where score is 1 - distance.
    """
    cv_vec = embed([cv_text])[0]

    with SessionLocal() as session:
        dist = Job.embedding.cosine_distance(cv_vec)
        rows = session.execute(
            select(Job.id, Job.title, Job.company, (1-dist).label("score"))
            .where(Job.embedding.is_not(None))
            .order_by(dist)
            .limit(top_k)
        ).all()

    return rows

    