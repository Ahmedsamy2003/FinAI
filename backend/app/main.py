from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.rag.pipeline import run_rag_pipeline


app = FastAPI(
    title="FinAI API",
    description="AI-powered financial analysis backend",
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================

class ChatRequest(BaseModel):
    question: str
    conversation_id: str = "default"
    top_k: int = 4


class ChatResponse(BaseModel):
    answer: str
    type: str = "rag"
    intent: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    chart: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "FinAI API",
    }


# =========================================================
# CHAT ENDPOINT
# =========================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:

        response = run_rag_pipeline(
            question=question,
            conversation_id=request.conversation_id,
            top_k=request.top_k,
        )

        # -------------------------------------------------
        # Backward compatibility
        # -------------------------------------------------
        #
        # If the pipeline still returns a plain string,
        # treat it as a normal RAG response.
        #

        if isinstance(response, str):
            return ChatResponse(
                answer=response,
                type="rag",
            )

        # -------------------------------------------------
        # Structured pipeline response
        # -------------------------------------------------

        return ChatResponse(
            answer=response.get("answer", ""),
            type=response.get("type", "rag"),
            intent=response.get("intent"),
            parameters=response.get("parameters"),
            result=response.get("result"),
            chart=response.get("chart"),
            analysis=response.get("analysis"),
        )

    except Exception as e:

        print(f"[FinAI API ERROR] {e}")

        raise HTTPException(
            status_code=500,
            detail="FinAI failed to generate a response.",
        )