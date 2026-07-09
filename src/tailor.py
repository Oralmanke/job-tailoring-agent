from datetime import date
from pathlib import Path

from src.llm import generate, parse_json
from src.render import render_cover_letter, render_cv
from src.prompts import CL_RULES, CV_RULES
from src.evaluator import evaluate, skills_from_cv
from src.logger import get_logger

log = get_logger(__name__)


def tailor_cv(cv_markdown: str, job) -> dict:
    prompt = f"CV (markdown):\n{cv_markdown}\n\nJOB:\n{job.title} at {job.company}\n{job.description}"
    return parse_json(generate(prompt=prompt,system=CV_RULES))

def cv_to_text(cv: dict) -> str:
    parts = [cv["professional_summary"]]
    for e in cv["experience"]:
        parts.append(f"{e['role']} @ {e['company']}: " + "; ".join(e["bullets"]))
    for p in cv["projects"]:
        parts.append(f"{p['name']}: " + "; ".join(p["bullets"]))
    parts.append("Skills: " + ", ".join(cv["technical_skills"].values()))
    return "\n".join(parts)


def write_cover_letter(cv: dict, job) -> dict:
    prompt = f"TAILORED CV:\n{cv_to_text(cv)}\n\nJOB:\n{job.title} at {job.company}\n{job.description}"
    cl = parse_json(generate(prompt, system=CL_RULES))
    cl.update({                                  
        "candidate_name": cv["candidate_name"], "email": cv["email"],
        "phone": cv["phone"], "location": cv["location"],
        "company": job.company, "date": date.today().strftime("%B %d, %Y"),
    })
    return cl


def tailor_for_job(cv_markdown: str, job, out_dir: Path) -> tuple[Path, Path] | None:
    """Tailor a CV and cover letter for one job, writing .docx files to out_dir.

    Returns ``(cv_path, cl_path)`` on success, or ``None`` if either document
    fails the coverage/consistency checks.
    """
    cv = tailor_cv(cv_markdown, job)
    cv_text = cv_to_text(cv)
    skills = skills_from_cv(cv) 

    cv_report = evaluate(cv_markdown, cv_text, job, skills)

    if not cv_report["passed"]:
        log.info("CV rejected for %s: %s", job.title, cv_report["issues"])
        return None

    cv_path = render_cv(cv, job, out_dir)

    cl = write_cover_letter(cv, job)  # write_cover_letter expects the CV dict, not its text
    cover_text = " ".join(cl["body_paragraphs"])

    cl_report = evaluate(cv_text, cover_text, job, skills)
    if not cl_report["passed"]:
        log.info("Cover letter rejected for %s: %s", job.title, cl_report["issues"])
        return None

    cl_path = render_cover_letter(cl, job, out_dir)
    return cv_path, cl_path

