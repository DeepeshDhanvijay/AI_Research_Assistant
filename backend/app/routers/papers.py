import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from app.core.config import settings
from app.services.ingestion import ingest_paper, compute_file_hash
from app.services.chunking import chunk_text
from app.services.vector_store import add_paper_chunks
from app.services.paper_registry import register_paper, list_papers, get_paper, find_by_hash
from app.schemas.paper import UploadResponse

router = APIRouter(prefix="/papers", tags=["papers"])

@router.post("/upload", response_model=UploadResponse)
def upload_paper(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    dest_path = settings.papers_dir / file.filename
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_hash = compute_file_hash(dest_path)
    existing = find_by_hash(file_hash)
    if existing:
        dest_path.unlink()  # remove the redundant copy we just saved
        return UploadResponse(
            paper_id=existing["paper_id"],
            filename=existing["filename"],
            title=existing["title"],
            num_pages=existing["num_pages"],
            chunks_created=0,
            status="duplicate — already in the collection",
        )

    metadata, text = ingest_paper(dest_path, file.filename)
    chunks = chunk_text(text, metadata.paper_id)
    add_paper_chunks(chunks)
    register_paper(metadata)

    return UploadResponse(
        paper_id=metadata.paper_id,
        filename=metadata.filename,
        title=metadata.title,
        num_pages=metadata.num_pages,
        chunks_created=len(chunks),
        status="uploaded",
    )

@router.get("/")
def get_papers():
    return list_papers()

@router.get("/{paper_id}")
def get_paper_details(paper_id: str):
    paper = get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")
    return paper