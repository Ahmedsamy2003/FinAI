from fastapi import APIRouter
from pydantic import BaseModel

from backend.app.rag.pipeline import run_rag_pipeline


router = APIRouter(prefix="/api", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = run_rag_pipeline(
        question=request.message,
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        response=answer
    )