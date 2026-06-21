from src.db.database import init_db, save_jobs
from src.scraper.remotive import fetch_remotive  
from src.scraper.adzuna import fetch_adzuna

init_db()                       
jobs_remotive = fetch_remotive()  
jobs_adzuna = fetch_adzuna()             
save_jobs(jobs_remotive)
save_jobs(jobs_adzuna)  