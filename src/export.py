import shutil
import subprocess
from pathlib import Path

from src.logger import get_logger

log = get_logger(__name__)


def _find_soffice() -> str | None:
    """Locate a LibreOffice/soffice binary on PATH, if one exists."""
    for name in ("libreoffice", "soffice"):
        path = shutil.which(name)
        if path:
            return path
    return None


def to_pdf(docx_path: Path) -> Path:
    """Convert a .docx file to .pdf next to the original.

    Uses a headless LibreOffice conversion (available in the Docker image).
    Raises RuntimeError if LibreOffice is not installed, so the API layer can
    surface an honest error instead of returning the wrong file type.
    """
    docx_path = Path(docx_path)
    pdf_path = docx_path.with_suffix(".pdf")
    if pdf_path.exists():
        return pdf_path

    soffice = _find_soffice()
    if not soffice:
        raise RuntimeError(
            "PDF export requires LibreOffice, which was not found on PATH."
        )

    log.info("Converting %s to PDF via LibreOffice", docx_path.name)
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(docx_path.parent), str(docx_path)],
        check=True,
        capture_output=True,
    )
    if not pdf_path.exists():
        raise RuntimeError(f"PDF conversion did not produce {pdf_path}")
    return pdf_path
