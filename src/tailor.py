from openai import OpenAI
from anthropic import Anthropic
from src.config import settings
import json
from datetime import date
from src.render import render_cover_letter,render_cv
from pathlib import Path
from src.prompts import CL_RULES,CV_RULES
from src.evaluator import evaluate,skills_from_cv

_clients = {}

def get_client(provider: str):

    if provider not in _clients:
        if provider == "ollama":
            _clients[provider] = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        elif provider == "openai":
            _clients[provider] = OpenAI(api_key=settings.openai_api_key)
        elif provider == "anthropic":
            _clients[provider] = Anthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    return _clients[provider]
    

def generate(prompt: str, system: str, provider: str = None,
             temperature: float = 0.2, max_tokens: int = 1024) -> str:

    provider = provider or settings.llm_provider
    client = get_client(provider)

    if provider == "anthropic":              # settings.llm_provider DEĞİL → provider
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            system=system,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,           # artık parametre
            temperature=temperature,
        )
        return resp.content[0].text
    else:
        resp = client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content


def parse_json(raw: str) -> dict:               
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].removeprefix("json").strip()
    return json.loads(raw)


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


def tailor_for_job(cv_markdown: str, job, out_dir: Path):
    cv = tailor_cv(cv_markdown, job)
    cv_text = cv_to_text(cv)
    skills = skills_from_cv(cv) 

    cv_report = evaluate(cv_markdown, cv_text, job, skills)

    if not cv_report["passed"]:
        print(f"CV rejected {job.title}: {cv_report['issues']}")
        return None

    cv_path = render_cv(cv, job, out_dir)

    cl = write_cover_letter(cv_text, job)
    cover_text = " ".join(cl["body_paragraphs"])

    cl_report = evaluate(cv_text, cover_text, job, skills)
    if not cl_report["passed"]:
        print(f"Cover letter rejected {job.title}: {cl_report['issues']}")
        return None

    cl_path = render_cover_letter(cl, job, out_dir)
    return cv_path, cl_path

