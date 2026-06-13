import requests
from src.config import settings

#TODO: make parameter that take users title adn pass it to what in get function params. Also with whıch country 

def fetch_remotive():

    jobs = []

    base_url = "https://remotive.com/api/remote-jobs"

    resp = requests.get(base_url, params={"search": "ai ml software", "limit": 100}, timeout=10)
    
    resp.raise_for_status()

    data = resp.json()

    for job in data["jobs"]:

        ordered_data = {
            "title": job.get("title"),
            "company": job.get("company_name"),
            "description": job.get("description"),
            "location": job.get("candidate_required_location"),
            "url": job.get("url"),
            "source": "remotive",
            "created": job.get("publication_date")
        }

        jobs.append(ordered_data)

    return jobs

fetch_remotive()