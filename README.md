# Datasheet Assistant — Multimodal RAG

A RAG system over electronics datasheets (ESP32, sensor ICs, op-amps,
voltage regulators) that extracts and indexes text, tables, and diagrams
separately, instead of treating a datasheet as one long string of text.

## Why this exists

Standard RAG chunks PDFs as plain text and misses the pin configuration
tables and wiring diagrams that make up a large part of any real
datasheet. This project measures that failure directly: a text-only
baseline is built first, then compared against a multimodal pipeline that
extracts tables (`pdfplumber`) and diagrams (OpenCV + OCR + vision
captioning) as separate, purpose-built retrieval paths.

## Results

| Category | Baseline (text-only) | Multimodal |
|---|---|---|
| Text questions | TBD | TBD |
| Table questions | TBD | TBD |
| Diagram questions | TBD | TBD |

Fill this in after running `src/eval/run_eval.py` against both pipelines.

## Architecture

```
PDF datasheets
  ├── Text chunks     ──┐
  ├── Tables (markdown) ──┼── Qdrant (3 collections) ── Rerank ── Claude ── Answer
  └── Diagrams (OCR + caption) ┘
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your ANTHROPIC_API_KEY

docker compose up -d   # starts the API + Qdrant
```

Run the frontend separately:
```bash
streamlit run frontend/app.py
```

## Project structure

See `docs/BUILD_PLAN.md` for the full week-by-week build plan, including
the reasoning behind each design decision and the code for every stage.

```
src/ingest/     PDF extraction: text, tables, diagrams
src/embed/      Sentence-transformer embedding wrapper
src/retrieve/   Qdrant vector store + cross-encoder reranker
src/generate/   Prompting and answer generation
src/eval/       Baseline vs multimodal evaluation harness
src/api/        FastAPI serving layer
frontend/       Streamlit demo UI
data/           Datasheets and the eval question set (PDFs gitignored)
```

## Status

- [ ] Baseline text-only pipeline
- [ ] Eval set written (40 questions: text / table / diagram)
- [ ] Multimodal extraction (tables + diagrams)
- [ ] Unified retrieval across 3 collections + reranking
- [ ] Baseline vs multimodal comparison run and documented
- [ ] Confidence threshold / refusal behavior
- [ ] Streamlit frontend with source grounding
- [ ] Deployed on AWS
