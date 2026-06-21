from src.db.database import SessionLocal
from src.db.models import Job

with SessionLocal() as session:
    remotive = 0
    adzuna = 0
    print("Jobs quantity", session.query(Job).count())
    for job in session.query(Job):
        if job.source == "remotive":
            remotive += 1
        elif job.source == "adzuna":
            adzuna += 1
    print(adzuna)
    print(remotive)