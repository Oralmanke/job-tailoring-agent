"""Unit tests for the pure evaluation helpers.

These never touch the network or the DB. The one function that would call an
LLM (``judge`` via ``evaluate``) is monkeypatched so the tests stay fast and
free.
"""
from types import SimpleNamespace

from src import evaluator
from src.evaluator import coverage, skill_terms, skills_from_cv


def test_skills_from_cv_splits_and_normalizes():
    cv = {"technical_skills": {"lang": "Python, SQL ,  Go", "cloud": "AWS"}}
    assert skills_from_cv(cv) == {"python", "sql", "go", "aws"}


def test_skills_from_cv_ignores_empty_fragments():
    cv = {"technical_skills": {"lang": "Python, , ,"}}
    assert skills_from_cv(cv) == {"python"}


def test_skill_terms_matches_case_insensitively():
    desc = "We need strong Python and Kubernetes experience."
    skills = {"python", "kubernetes", "rust"}
    assert skill_terms(desc, skills) == {"python", "kubernetes"}


def test_coverage_full_when_all_terms_present():
    assert coverage("python and sql developer", {"python", "sql"}) == 1.0


def test_coverage_partial():
    assert coverage("python only", {"python", "sql"}) == 0.5


def test_coverage_empty_terms_returns_one():
    # No terms to check against -> nothing is "missing".
    assert coverage("anything", set()) == 1.0


def test_evaluate_skips_coverage_when_no_skills(monkeypatch):
    """With an empty skills set the coverage gate must be skipped entirely."""
    called = {"judge": False}

    def fake_judge(source, generated):
        called["judge"] = True
        return {"consistent": True, "issues": []}

    monkeypatch.setattr(evaluator, "judge", fake_judge)

    job = SimpleNamespace(title="ML Engineer", company="Acme", description="build models")
    report = evaluator.evaluate("source", "unrelated text", job, skills=set())

    assert called["judge"] is True          # went straight to the judge
    assert report["coverage"] is None        # coverage not computed
    assert report["passed"] is True


def test_evaluate_rejects_on_low_coverage(monkeypatch):
    """When skills exist and coverage is below threshold, reject before judging."""
    monkeypatch.setattr(
        evaluator, "judge",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("judge must not run")),
    )
    job = SimpleNamespace(title="ML Engineer", description="python tensorflow")
    report = evaluator.evaluate("source", "totally unrelated", job, skills={"python"})

    assert report["passed"] is False
    assert report["issues"] == ["coverage too low"]
