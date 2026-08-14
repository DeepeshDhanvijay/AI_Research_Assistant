import uuid
import re
from datetime import datetime, timezone
from pathlib import Path
import hashlib

import pymupdf  # replaces: import fitz as fitz

from app.core.config import settings
from app.schemas.paper import PaperMetadata

def extract_text_and_metadata(pdf_path: Path) -> tuple[str, dict]:
    """Extract full text and basic metadata from a PDF using pymupdf."""
    doc = pymupdf.open(pdf_path)

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    title = doc.metadata.get("title") or None
    if not title:
        title = _guess_title(full_text)

    metadata = {
        "num_pages": doc.page_count,
        "title": title,
    }
    doc.close()

    return full_text, metadata

def _guess_title(text: str) -> str | None:
    """
    Best-effort title guess: first substantial line that doesn't look like a
    journal header, ISSN line, or DOI reference.
    """
    skip_patterns = re.compile(r'ISSN|DOI|VOLUME|ISSUE|\bJOURNAL\b|©|www\.', re.IGNORECASE)

    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 15 or len(line) > 200:
            continue
        if skip_patterns.search(line):
            continue
        return line

    return None

def clean_text(text: str) -> str:
    """Same reference-stripping + whitespace cleanup lesson learned in Project 1/2."""
    pattern = r'\n\s*R\s*E\s*F\s*E\s*R\s*E\s*N\s*C\s*E\s*S?\s*\n|\n\s*B\s*I\s*B\s*L\s*I\s*O\s*G\s*R\s*A\s*P\s*H\s*Y\s*\n'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        text = text[:match.start()]

    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return " ".join(lines)

def compute_file_hash(file_path: Path) -> str:
    """Content hash — used to detect re-uploads of the same file, even under a different filename."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()[:16]

def ingest_paper(file_path: Path, original_filename: str) -> tuple[PaperMetadata, str]:
    raw_text, extracted_meta = extract_text_and_metadata(file_path)
    cleaned = clean_text(raw_text)
    file_hash = compute_file_hash(file_path)

    paper_id = str(uuid.uuid4())[:8]

    metadata = PaperMetadata(
        paper_id=paper_id,
        filename=original_filename,
        title=extracted_meta["title"],
        num_pages=extracted_meta["num_pages"],
        uploaded_at=datetime.now(timezone.utc),
        char_count=len(cleaned),
        file_hash=file_hash,
    )

    return metadata, cleaned


if __name__ == "__main__":
    # Quick manual test — place any PDF in data/papers/ first
    sample_files = list(settings.papers_dir.glob("*.pdf"))
    if not sample_files:
        print(f"No PDFs found in {settings.papers_dir} — add one to test.")
    else:
        metadata, text = ingest_paper(sample_files[0], sample_files[0].name)
        print(f"Paper ID: {metadata.paper_id}")
        print(f"Title: {metadata.title}")
        print(f"Pages: {metadata.num_pages}")
        print(f"Characters after cleaning: {metadata.char_count}")
        print(f"\nPreview: {text[:200]}...")