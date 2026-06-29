from src.prompts import JUDGE_RULES
from src.tailor import generate, parse_json, cv_to_text


def skills_from_cv(cv:dict) -> set[str]:
    terms = set()
    for skilss_str in cv["technical_skills"].values():
        for skill in skilss_str.split(","):
            cleaned = skill.strip().lower()
            if cleaned:
                terms.add(cleaned)

    return terms

def skill_terms(description: str, skills: set[str]) -> set[str]:
    text = description.lower()
    return {s for s in skills if s in text}

def coverage(text: str, terms: set[str]) -> float:

    if not terms:
        return 1.0
    
    found = {t for t in terms if t in text.lower()}
    
    return len(found) / len(terms)

def judge(source: str, generated: str) -> dict:
    prompt = f"SOURCE:\n{source}\n\nGENERATED:\n{generated}"
    return parse_json(generate(prompt, JUDGE_RULES, provider="anthropic", temperature=0,max_tokens= 512))

def evaluate(source: str, generated: str, job, skills: set[str]) -> dict:
    
    terms = {w.lower() for w in job.title.split()} | skill_terms(job.description, skills)
    
    cov = coverage(generated, terms)

    if cov < 0.5:
        return {
            "coverage": round(cov, 2),
            "consistent": None,                 
            "issues": ["coverage too low"],
            "passed": False,
        }

    verdict = judge(source, generated)

    return {
        "coverage": round(cov, 2),
        "consistent": verdict["consistent"],
        "issues": verdict["issues"],
        "passed": verdict["consistent"],
    }

