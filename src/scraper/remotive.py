from src.config import settings
from src.scraper.base import BaseScraper


class RemotiveScraper(BaseScraper):
    """Fetch remote jobs from the Remotive API.

    Remotive is global, so ``country`` is accepted for a uniform interface but
    not sent to the API.
    """

    source = "remotive"

    def _build_request(self) -> tuple[str, dict]:
        params = {"search": self.search, "limit": self.limit}
        return settings.remotive_base_url, params

    def _iter_raw(self, payload: dict) -> list[dict]:
        return payload.get("jobs", [])

    def normalize(self, raw: dict) -> dict:
        return {
            "title": raw.get("title"),
            "company": raw.get("company_name"),
            "description": raw.get("description"),
            "location": raw.get("candidate_required_location"),
            "url": raw.get("url"),
            "source": self.source,
            "created": raw.get("publication_date"),
        }


def fetch_remotive(
    search: str | None = None,
    country: str | None = None,
    limit: int | None = None,
) -> list[dict]:
    """Convenience wrapper kept for backwards compatibility with the pipeline."""
    return RemotiveScraper(search=search, country=country, limit=limit).fetch()
