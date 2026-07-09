from src.config import settings
from src.scraper.base import BaseScraper


class AdzunaScraper(BaseScraper):
    """Fetch jobs from the Adzuna search API for a given country."""

    source = "adzuna"

    def _build_request(self) -> tuple[str, dict]:
        url = f"{settings.adzuna_base_url}/{self.country}/search/1"
        params = {
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "what": self.search,
            "results_per_page": self.limit,
            "sort_by": "date",
        }
        return url, params

    def _iter_raw(self, payload: dict) -> list[dict]:
        return payload.get("results", [])

    def normalize(self, raw: dict) -> dict:
        return {
            "title": raw.get("title"),
            "company": raw.get("company", {}).get("display_name"),
            "description": raw.get("description"),
            "location": raw.get("location", {}).get("display_name"),
            "url": raw.get("redirect_url"),
            "source": self.source,
            "created": raw.get("created"),
        }


def fetch_adzuna(
    search: str | None = None,
    country: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Convenience wrapper kept for backwards compatibility with the pipeline."""
    return AdzunaScraper(search=search, country=country, limit=limit).fetch()
