from abc import ABC, abstractmethod

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.logger import get_logger

log = get_logger(__name__)


class BaseScraper(ABC):
    """Common contract for every job source.
    """

    #: Human-readable source tag stored on each job row.
    source: str = "base"

    def __init__(
        self,
        search: str | None = None,
        country: str | None = None,
        limit: int | None = None,
    ) -> None:
        self.search = search or settings.search_query
        self.country = country or settings.country
        self.limit = limit or settings.results_per_page

    @abstractmethod
    def _build_request(self) -> tuple[str, dict]:
        """Return (url, query_params) for this source's search request."""

    @abstractmethod
    def _iter_raw(self, payload: dict) -> list[dict]:
        """Extract the list of raw job records from the API response body."""

    @abstractmethod
    def normalize(self, raw: dict) -> dict:
        """Map one raw record to our common job dict shape."""

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _get(self, url: str, params: dict) -> dict:
        """GET with automatic retry/backoff on transient failures."""
        resp = requests.get(url, params=params, timeout=settings.http_timeout)
        resp.raise_for_status()
        return resp.json()

    def fetch(self) -> list[dict]:
        """Fetch and normalize jobs from this source.

        Returns a list of dicts matching the ``Job`` columns. A single failing
        record is skipped and logged rather than aborting the whole batch.
        """
        url, params = self._build_request()
        log.info("Fetching %s jobs (search=%r country=%r limit=%s)",
                 self.source, self.search, self.country, self.limit)
        payload = self._get(url, params)

        jobs: list[dict] = []
        for raw in self._iter_raw(payload):
            try:
                jobs.append(self.normalize(raw))
            except (KeyError, TypeError) as exc:
                log.warning("Skipping malformed %s record: %s", self.source, exc)
        log.info("Fetched %s %s jobs", len(jobs), self.source)
        return jobs
