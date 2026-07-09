"""Tests for scraper parameterization and normalization (no network calls)."""
from src.config import settings
from src.scraper.adzuna import AdzunaScraper
from src.scraper.remotive import RemotiveScraper


def test_defaults_come_from_settings():
    s = AdzunaScraper()
    assert s.search == settings.search_query
    assert s.country == settings.country
    assert s.limit == settings.results_per_page


def test_explicit_params_override_defaults():
    s = RemotiveScraper(search="rust backend", country="uk", limit=5)
    assert (s.search, s.country, s.limit) == ("rust backend", "uk", 5)


def test_adzuna_request_uses_country_and_search():
    url, params = AdzunaScraper(search="data science", country="fr")._build_request()
    assert "/fr/search/1" in url
    assert params["what"] == "data science"


def test_adzuna_normalize_maps_nested_fields():
    raw = {
        "title": "ML Engineer",
        "company": {"display_name": "Acme"},
        "description": "Build models",
        "location": {"display_name": "Berlin"},
        "redirect_url": "https://x/1",
        "created": "2024-01-01T00:00:00Z",
    }
    out = AdzunaScraper().normalize(raw)
    assert out["company"] == "Acme"
    assert out["location"] == "Berlin"
    assert out["url"] == "https://x/1"
    assert out["source"] == "adzuna"


def test_remotive_normalize_maps_flat_fields():
    raw = {
        "title": "Backend Dev",
        "company_name": "Globex",
        "description": "APIs",
        "candidate_required_location": "Remote",
        "url": "https://y/2",
        "publication_date": "2024-02-02",
    }
    out = RemotiveScraper().normalize(raw)
    assert out["company"] == "Globex"
    assert out["location"] == "Remote"
    assert out["source"] == "remotive"
