from fastapi import APIRouter
from pydantic import BaseModel

from app.services.summarization_service import summarize_paper
from app.services.comparison_service import compare_papers
from app.services.relationship_service import find_relationships
from app.services.extraction_service import extract_methodology_and_results, extract_citations

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/summarize/{paper_id}")
def summarize(paper_id: str):
    return {"paper_id": paper_id, "summary": summarize_paper(paper_id)}

class CompareRequest(BaseModel):
    paper_id_a: str
    paper_id_b: str

@router.post("/compare")
def compare(request: CompareRequest):
    return compare_papers(request.paper_id_a, request.paper_id_b)

@router.get("/relationships/{paper_id}")
def relationships(paper_id: str):
    return find_relationships(paper_id)

@router.get("/methodology-results/{paper_id}")
def methodology_results(paper_id: str):
    return extract_methodology_and_results(paper_id)

@router.get("/citations/{paper_id}")
def citations(paper_id: str):
    return extract_citations(paper_id)

class LitReviewRequest(BaseModel):
    paper_ids: list[str] | None = None

@router.post("/literature-review")
def literature_review(request: LitReviewRequest):
    from app.services.comparison_service import generate_literature_review
    return generate_literature_review(request.paper_ids)
