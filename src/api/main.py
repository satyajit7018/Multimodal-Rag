"""FastAPI Serving Layer for Datasheet Assistant.
Provides endpoints for multimodal queries, visual grounding assets,
circuit compatibility validation, pin-to-pin wiring generation, PDF uploads, and benchmark reports.
"""

from __future__ import annotations
import os
import json
import datetime
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from src.retrieve.multimodal_search import search_multimodal_parallel, search_baseline
from src.generate.llm import answer_with_confidence
from src.engine.circuit_validator import validate_circuit_compatibility, COMPONENT_REGISTRY
from src.engine.wiring_assistant import generate_wiring_plan

app = FastAPI(
    title="Datasheet Assistant — Scaled Multimodal RAG API",
    description="Multi-Model Datasheet Assistant powered by Claude Opus 4.6 CTO & Gemini 3.7 Flash Subagents.",
    version="2.0.0",
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
RAW_PDF_DIR = "data/raw_pdfs"


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


class CircuitValidateRequest(BaseModel):
    components: List[str]


class WiringRequest(BaseModel):
    host_mcu: str
    peripherals: List[str]


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: str  # "thumbs_up" or "thumbs_down"
    notes: Optional[str] = ""


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "arch": "Dual-Tier Multi-Model (Claude Opus 4.6 CTO + Gemini 3.7 Subagents)",
        "components_registered": len(COMPONENT_REGISTRY),
    }


@app.get("/components")
def list_components():
    """Lists all registered components and their metadata."""
    return {"components": COMPONENT_REGISTRY}


@app.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest):
    """Executes datasheet retrieval and answer generation."""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if req.mode == "baseline":
        hits = search_baseline(question, top_k=3)
        contexts = [h["content"] for h in hits]
        answer, conf = answer_with_confidence(question, hits, contexts)
        is_refusal = conf < 0.35

        return QueryResponse(
            question=question,
            answer=answer,
            confidence_score=round(conf, 3),
            is_refusal=is_refusal,
            source_table=None,
            source_table_meta=None,
            source_image_url=None,
            source_image_meta=None,
            retrieved_contexts=contexts,
        )

    # Multimodal Mode (3 collections + cross-encoder rerank)
    mm_result = search_multimodal_parallel(question, top_k_per_modality=3, top_rerank=5)
    contexts = mm_result["ranked_contexts"]
    answer, conf = answer_with_confidence(question, mm_result["all_hits"], contexts)
    is_refusal = conf < 0.35

    image_url = None
    if mm_result["source_image"]:
        base_name = os.path.basename(mm_result["source_image"])
        image_url = f"/static/images/{base_name}"

    return QueryResponse(
        question=question,
        answer=answer,
        confidence_score=round(conf, 3),
        is_refusal=is_refusal,
        source_table=mm_result["source_table"],
        source_table_meta=mm_result["source_table_meta"],
        source_image_url=image_url,
        source_image_meta=mm_result["source_image_meta"],
        retrieved_contexts=contexts,
    )


@app.post("/circuit/validate")
def validate_circuit(req: CircuitValidateRequest):
    """Audits multi-component selections for I2C collisions, logic level mismatches, and power load."""
    return validate_circuit_compatibility(req.components)


@app.post("/circuit/wire")
def get_circuit_wiring(req: WiringRequest):
    """Generates pin-to-pin wiring map between host MCU and peripheral chips."""
    return generate_wiring_plan(req.host_mcu, req.peripherals)


@app.post("/upload/pdf")
async def upload_datasheet_pdf(file: UploadFile = File(...)):
    """Uploads a PDF datasheet and indexes it into the multimodal collections."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(RAW_PDF_DIR, exist_ok=True)
    save_path = os.path.join(RAW_PDF_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger subagents to index the new PDF
    from src.ingest.ingest_multimodal import process_single_pdf_multimodal
    from src.embed.embedder import Embedder
    from src.retrieve.vector_store import VectorStore

    t_rec, tab_rec, img_rec = process_single_pdf_multimodal(save_path)
    embedder = Embedder()

    if t_rec:
        VectorStore("multimodal_text").upsert([abs(hash(r["content"])) % 100000 for r in t_rec], embedder.embed([r["content"] for r in t_rec]), t_rec)
    if tab_rec:
        VectorStore("multimodal_tables").upsert([abs(hash(r["embed_text"])) % 100000 for r in tab_rec], embedder.embed([r["embed_text"] for r in tab_rec]), tab_rec)
    if img_rec:
        VectorStore("multimodal_images").upsert([abs(hash(r["embed_text"])) % 100000 for r in img_rec], embedder.embed([r["embed_text"] for r in img_rec]), img_rec)

    return {
        "status": "success",
        "filename": file.filename,
        "extracted": {
            "text_chunks": len(t_rec),
            "tables": len(tab_rec),
            "diagrams": len(img_rec),
        }
    }


@app.post("/feedback")
def log_feedback(fb: FeedbackRequest):
    """Logs user feedback for continuous improvement and quality monitoring."""
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "question": fb.question,
        "answer": fb.answer,
        "rating": fb.rating,
        "notes": fb.notes,
    }
    with open(FEEDBACK_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"status": "success", "message": "Feedback recorded successfully."}


@app.get("/eval/results")
def get_eval_results():
    """Returns stored dual evaluation benchmark metrics."""
    res_path = "data/eval_results.json"
    if not os.path.exists(res_path):
        raise HTTPException(status_code=404, detail="Benchmark results not found.")
    with open(res_path, "r") as f:
        return json.load(f)
