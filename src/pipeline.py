from src.matcher import cv_match
from src.db.database import init_db, save_jobs,SessionLocal
from src.scraper.remotive import fetch_remotive  
from src.scraper.adzuna import fetch_adzuna
from pathlib import Path
from src.db.models import Job
from src.tailor import tailor_for_job

def ingest_jobs():
    init_db()                         
    save_jobs(fetch_remotive())
    save_jobs(fetch_adzuna())  

def tailor_top_matches(cv: Path, n: int = 3):
    cv_md = Path(cv).read_text(encoding="utf-8")
    results = cv_match(cv_md)
    out = Path("output")
    out.mkdir(exist_ok=True)

    with SessionLocal() as session:
        for r in results[:n]:
            job = session.get(Job, r.id)
            try:
                result = tailor_for_job(cv_md, job, out)
                if result is None:                                    
                    print(f"Skipped {job.title}: rejected by checks")
                else:                                                 
                    cv_path_out, cl_path_out = result
                    print("OK:", cv_path_out.name,"\n", cl_path_out)
            except Exception as e:
                print(f"Passed {job.title}: {e}")
