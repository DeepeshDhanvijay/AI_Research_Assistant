from fastapi import APIRouter
from pydantic import BaseModel

from app.services.qa_service import answer_question

router = APIRouter(prefix="/qa", tags=["qa"])

class QuestionRequest(BaseModel):
    query: str
    paper_id: str | None = None

@router.post("/ask")
def ask(request: QuestionRequest):
    return answer_question(request.query, request.paper_id)