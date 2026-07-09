from src.prompts import JUDGE_RULES
from src.llm import generate, parse_json
from src.config import settings


def skills_from_cv(cv:dict) -> set[str]:
    terms = set()
    # .get(...) yerine köşeli parantez kullansaydık, CV'de "technical_skills"
    # anahtarı hiç yoksa KeyError ile çökerdik. .get ile yoksa boş sözlük varsayıp
    # boş küme döndürüyoruz (evaluate bu durumda coverage kapısını atlıyor).
    for skilss_str in cv.get("technical_skills", {}).values():
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
    """Gate a generated document by keyword coverage, then LLM fact-check."""
    if skills:
        terms = {w.lower() for w in job.title.split()} | skill_terms(job.description, skills)
        cov = coverage(generated, terms)

        if cov < settings.coverage_threshold:
            return {
                "coverage": round(cov, 2),
                "consistent": None,
                "issues": ["coverage too low"],
                "passed": False,
            }
    else:
        cov = None  # coverage gate skipped: no skills to measure against

    verdict = judge(source, generated)

    return {
        "coverage": round(cov, 2) if cov is not None else None,
        "consistent": verdict["consistent"],
        "issues": verdict["issues"],
        "passed": verdict["consistent"],
    }

