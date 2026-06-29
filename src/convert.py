from pathlib import Path
from markitdown import MarkItDown

md = MarkItDown()

def to_markdown(file_path: Path) -> Path:

    if not file_path.exists():
        raise FileNotFoundError(f"Can not find file: {file_path}")
    
    if file_path.suffix == ".md":
        return file_path

    result = md.convert(str(file_path))
    output = file_path.with_suffix(".md")
    output.write_text(result.text_content, encoding="utf-8")

    return output