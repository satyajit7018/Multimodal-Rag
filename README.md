# Datasheet Assistant — Multimodal RAG with Multi-Model CTO Architecture

A production-grade Multimodal Retrieval-Augmented Generation (RAG) system over electronics datasheets (ESP32, sensor ICs, op-amps, voltage regulators, motor drivers) that indexes text, tables, and diagrams into specialized vector collections, overseen by an **Executive CTO (Claude Opus 4.6)** and **Parallel Specialist Subagents (Gemini 3.7 Flash)**.

---

## 🚀 Benchmark Results (Baseline vs. Multimodal)

Tested across a 40-question benchmark (`data/eval_set.json`) covering general text, complex electrical specification tables, and pinout schematic diagrams:

| Category | Baseline (Text-Only) | Multimodal (CTO Squad) | Accuracy Gain |
| :--- | :---: | :---: | :---: |
| **Text Questions (15)** | 100.0% (15/15) | **100.0%** (15/15) | +0.0% |
| **Table Questions (15)** | 60.0% (9/15) | **86.7%** (13/15) | **+26.7%** |
| **Diagram Questions (10)** | 80.0% (8/10) | **100.0%** (10/10) | **+20.0%** |
| **OVERALL ACCURACY (40)** | **80.0% (32/40)** | **95.0% (38/40)** | **+15.0%** |

---

## 🏗️ Multi-Model Architecture

```
Datasheet PDF (ESP32, LM7805, LM358, BME280, DHT22, NE555, L298N, MAX485, STM32, PCA9685)
   │
   ├── Text Chunks (Layout-aware) ──────────────► Qdrant (multimodal_text)
   │
   ├── Tables (Markdown + Gemini 3.7 Summary) ──► Qdrant (multimodal_tables) ──┐
   │                                                                            │
   └── Diagrams (OpenCV Crop + BBox + OCR) ─────► Qdrant (multimodal_images) ──┤
                                                                               │
               User Query (Parallel Multi-Store Search) ───────────────────────┤
                                                                               ▼
                                                                     Cross-Encoder Reranker
                                                                               │
                                                                               ▼
                                                         CTO Executive Model (Claude Opus 4.6)
                                                                               │
                                                                  ┌────────────┴────────────┐
                                                                  ▼                         ▼
                                                           Confidence >= 0.35        Confidence < 0.35
                                                                  │                         │
                                                                  ▼                         ▼
                                                         Grounded Answer + Citations   Calibrated Refusal
                                                         [TEXT] [TABLE] [DIAGRAM]
```

### Multi-Model Subagent Hierarchy
- **Executive CTO (Claude Opus 4.6)**: Query decomposition, cross-modality evidence validation, hallucination prevention, citation attribution (`[TEXT]`, `[TABLE: Page X]`, `[DIAGRAM: Page Y]`), and confidence gating (< 0.35 calibrated refusal).
- **Vision Specialist Subagent (Gemini 3.7 Flash)**: Diagram extraction, schematic pinout mapping, and OpenCV bounding box validation.
- **Table Specialist Subagent (Gemini 3.7 Flash)**: `pdfplumber` multi-column table extraction, markdown formatting, and natural language semantic summarization.
- **Text Specialist Subagent (Gemini 3.7 Flash)**: Layout-aware document partitioning and recursive semantic chunking.

---

## ⚡ Quickstart

### 1. Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Generate Corpus & Ingest Datasheets
```bash
# Generate 10 target datasheets & diagram crops
python3 -m src.ingest.download_datasheets

# Ingest into baseline collection
python3 -m src.ingest.ingest_baseline

# Ingest into 3 parallel multimodal collections (Subagents)
python3 -m src.ingest.ingest_multimodal
```

### 3. Run Benchmark Evaluation
```bash
python3 -m src.eval.run_eval
```

### 4. Launch FastAPI Server & Streamlit UI
```bash
# Terminal 1: FastAPI Serving Layer
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Streamlit Interactive Grounding Demo
streamlit run frontend/app.py
```

---

## 📁 Repository Structure

```
├── data/
│   ├── raw_pdfs/              # 10 Reference PDF datasheets
│   ├── eval_set.json          # 40-question benchmark set (Text, Table, Diagram)
│   ├── eval_results.json      # Dual benchmark execution output
│   └── extracted/images/      # Cropped diagrams with bounding metadata
├── src/
│   ├── ingest/
│   │   ├── download_datasheets.py  # Corpus generator
│   │   ├── extract.py              # Text layout extraction
│   │   ├── table_extract.py        # Table specialist subagent
│   │   ├── image_extract.py        # Vision specialist subagent
│   │   ├── ingest_baseline.py      # Baseline ingestion runner
│   │   └── ingest_multimodal.py    # Parallel multimodal orchestrator
│   ├── embed/
│   │   └── embedder.py             # 384-d dense vector embedder
│   ├── retrieve/
│   │   ├── vector_store.py         # Qdrant wrapper (Embedded + Server mode)
│   │   ├── reranker.py             # Cross-encoder precision reranker
│   │   └── multimodal_search.py    # Parallel 3-store retrieval
│   ├── generate/
│   │   ├── providers.py            # Multi-model abstraction (Opus 4.6 + Gemini 3.7)
│   │   └── llm.py                  # CTO generation prompt & confidence refusal
│   ├── eval/
│   │   └── run_eval.py             # Dual pipeline benchmark harness
│   └── api/
│       └── main.py                 # FastAPI backend with static image mount
├── frontend/
│   └── app.py                     # Streamlit demo with visual grounding
├── tests/
│   └── test_components.py         # Pytest test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🌟 Project Status

- [x] Datasheet corpus generated (10 target components)
- [x] 40-Question balanced benchmark dataset (`data/eval_set.json`)
- [x] Baseline text-only pipeline indexed and tested
- [x] Multimodal parallel extraction (Text, Markdown Tables, Vision Diagrams)
- [x] Qdrant 3-collection indexing with zero-dependency embedded fallback
- [x] Executive CTO (Claude Opus 4.6) generation with origin citations & confidence refusal (< 0.35)
- [x] Dual benchmark evaluation executed (**+26.7% gain on Tables, +20.0% gain on Diagrams, 95% Overall**)
- [x] FastAPI REST API with static diagram image serving
- [x] Streamlit interactive demo with side-by-side visual grounding
- [x] Unit test suite passing (`pytest tests/`)
