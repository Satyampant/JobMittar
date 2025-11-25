"""File reading utilities for resume documents (PDF, DOCX, TXT)."""

import io
from typing import Union
from pathlib import Path


def read_resume_file(file_path: Union[str, Path]) -> str:
    """Read resume from PDF, DOCX, or TXT file."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == ".txt":
        return path.read_text(encoding="utf-8")
    elif ext == ".pdf":
        return _read_pdf(path)
    elif ext in [".docx", ".doc"]:
        return _read_docx(path)
    raise ValueError(f"Unsupported format: {ext}")


def _read_pdf(path: Path) -> str:
    """Extract text from PDF using pdfplumber."""
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _read_docx(path: Path) -> str:
    """Extract text from DOCX using python-docx."""
    import docx
    doc = docx.Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)
