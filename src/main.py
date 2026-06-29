from pathlib import Path
from src.pipeline import ingest_jobs, tailor_top_matches
from src.matcher import embed_jobs
from src.convert import to_markdown

ingest_jobs()
embed_jobs()                                
tailor_top_matches(to_markdown(Path("data/Oral_Yalcinpinar_CV.pdf")), n=3)