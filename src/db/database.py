from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import base
from src.config import settings
from sqlalchemy.dialects.postgresql import insert
from .models import Job

engine =  create_engine(settings.db_url)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    base.metadata.create_all(engine)
    

def save_jobs(jobs: list[dict]):

    with SessionLocal() as session:
        for job in jobs:
            stmt = (
                insert(Job).values(**job).on_conflict_do_nothing(index_elements=["url"])
            )

            session.execute(stmt)
        session.commit()