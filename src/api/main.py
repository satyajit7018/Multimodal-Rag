"""FastAPI Serving Layer for Datasheet Assistant.
Provides endpoints for multimodal queries, visual grounding assets,
pipeline ingestion triggers, and benchmark reporting.
"""

import os
import json
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from src.retrieve.multimodal_search import search_multimodal_parallel, search_baseline
from src.generate.llm import answer_with_confidence

app = FastAPI(
    title="Datasheet Assistant — Multimodal RAG API",
    description="Multi-Model Datasheet Assistant powered by Claude Opus 4.6 CTO & Gemini 3.7 Flash Subagents.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for cropped diagram images
STATIC_IMG_DIR = os.path.join(os.getcwd(), "data", "extracted", "images")
os.makedirs(STATIC_IMG_DIR, exist_ok=True)
app.mount("/static/images", StaticFiles(directory=STATIC_IMG_DIR), name="static_images")

FEEDBACK_LOG_PATH = "data/feedback_log.jsonl"


class QueryRequest(BaseModel):
    question: str
    mode: Optional[str] = "multimodal"  # "multimodal" or "baseline"


class QueryResponse(BaseModel):
    question: str
    answer: str
    confidence_score: float
    is_refusal: bool
    source_table: Optional[str] = None
    source_table_meta: Optional[Dict[str, Any]] = None
    source_image_url: Optional[str] = None
    source_image_meta: Optional[Dict[str, Any]] = None
    retrieved_contexts: List[str]


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    is_correct: bool
    comment: Optional[str] = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Datasheet Assistant Multimodal RAG",
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if req.mode == "baseline":
        hits = search_baseline(req.question, top_k=3)
        contexts = [h["content"] for h in hits]
        answer, score = answer_with_confidence(req.question, hits, contexts)
        is_refusal = "i do not have enough verified information" in answer.lower()
        return QueryResponse(
            question=req.question,
            answer=answer,
            confidence_score=round(score, 3),
            is_refusal=is_refusal,
            source_table=None,
            source_table_meta=None,
            source_image_url=None,
            source_image_meta=None,
            retrieved_contexts=contexts,
        )

    # Multimodal pipeline (default)
    search_res = search_multimodal_parallel(req.question, top_k_per_modality=3, top_rerank=5)
    contexts = search_res["ranked_contexts"]
    answer, score = answer_with_confidence(req.question, search_res["all_hits"], contexts)
    is_refusal = "i do not have enough verified information" in answer.lower()

    # Format image URL
    image_url = None
    if search_res["source_image"]:
        img_basename = os.path.basename(search_res["source_image"])
        image_url = f"/static/images/{img_basename}"

    return QueryResponse(
        question=req.question,
        answer=answer,
        confidence_score=round(score, 3),
        is_refusal=is_refusal,
        source_table=search_res["source_table"],
        source_table_meta=search_res["source_table_meta"],
        source_image_url=image_url,
        source_image_meta=search_res["source_image_meta"],
        retrieved_contexts=contexts,
    )


@app.post("/feedback")
def log_feedback(req: FeedbackRequest):
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
    entry = {
        "question": req.question,
        "answer": req.answer,
        "is_correct": req.is_correct,
        "comment": req.comment,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    with open(FEEDBACK_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"status": "feedback_recorded", "entry": entry}


@app.get("/eval/results")
def get_eval_results():
    eval_path = "data/eval_results.json"
    if os.path.exists(eval_path):
        with open(eval_path, "r") as f:
            return json.load(f)
    return {"status": "no_results_yet", "message": "Run src.eval.run_eval to generate benchmark results."}
