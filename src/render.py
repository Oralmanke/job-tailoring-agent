from docxtpl import DocxTemplate
from pathlib import Path
import re
from unidecode import unidecode



def slugify(s: str) -> str:
    s = re.sub(r"\s*\([^)]*[/\\][^)]*\)\s*", " ", s)
    s = unidecode(s)
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")


def render_cv(cv_data: dict, job, out_dir: Path) -> Path:
    tpl = DocxTemplate("app/templates/cv_template.docx")
    tpl.render(cv_data,autoescape=True)
    out = out_dir / f"CV_{slugify(cv_data['candidate_name'])}_{slugify(job.company)}.docx"
    tpl.save(out)
    return out

def render_cover_letter(cl_data: dict, job, out_dir: Path) -> Path:
    tpl = DocxTemplate("app/templates/cover_letter_template.docx")
    tpl.render(cl_data, autoescape=True)
    out = out_dir / f"cover_letter_{slugify(cl_data['candidate_name'])}_{slugify(job.title)}.docx"
    tpl.save(out)
    return out


