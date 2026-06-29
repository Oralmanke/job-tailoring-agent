from src.db.database import SessionLocal
from src.embedding import embed
from src.db.models import Job
from pathlib import Path
from src.convert import to_markdown
from sqlalchemy import select


def embed_jobs():
    texts = []
    with SessionLocal() as session:
        jobs_without_embed = session.query(Job).filter(Job.embedding.is_(None)).all()
        if not jobs_without_embed:
            print("All jobs embedded")
            return
        for job in jobs_without_embed:
            text = f"{job.title}. {job.description}"
            texts.append(text)
        
        for vec, job in zip(embed(texts),jobs_without_embed):
            job.embedding = vec
        session.commit()


def cv_match(cv_text: str, top_k: int = 50):

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

    