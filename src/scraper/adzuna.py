import requests
from src.config import settings

#TODO: make parameter that take users title adn pass it to what in get function params. Also with whıch country 



def fetch_adzuna():

    jobs = []

    base_url = "https://api.adzuna.com/v1/api/jobs/de/search/1"

    resp = requests.get(base_url, params={"app_id": settings.adzuna_app_id, "app_key": settings.adzuna_app_key, "what": "ai ml software", "results_per_page":100, "sort_by": "date"}, timeout=10)
    
    resp.raise_for_status()

    data = resp.json()

    for job in data["results"]:

        ordered_data = {
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "description": job.get("description"),
            "location": job.get("location", {}).get("display_name"),
            "url": job.get("redirect_url"),
            "source": "adzuna",
            "created": job.get("created")
        }

        jobs.append(ordered_data)
    
    return jobs

fetch_adzuna()