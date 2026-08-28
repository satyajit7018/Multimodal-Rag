# Datasheet Assistant Pro — Scaled Multimodal RAG with Multi-Model CTO Architecture

An industrial-grade Multimodal Retrieval-Augmented Generation (RAG) system spanning **32 component datasheets across 6 electronics families**, with **105 curated evaluation questions**, automated **circuit compatibility checking**, **live pin-to-pin wiring diagrams**, **BM25 hybrid search**, and **one-click PDF design report exports**.

Overseen by an **Executive CTO (Claude Opus 4.6)** and **Parallel Specialist Subagents (Gemini 3.7 Flash)**.

---

## 🚀 105-Question Benchmark Results (Baseline vs. Multimodal)

Tested across a comprehensive 105-question benchmark (`data/eval_set.json`) covering general text architecture, complex electrical specification tables, pinout schematic diagrams, and comparative cross-datasheet circuit reasoning:

| Category | Baseline (Text-Only) | Multimodal (CTO Squad) | Accuracy Gain |
| :--- | :---: | :---: | :---: |
| **Text Questions (38)** | 84.2% (32/38) | **86.8%** (33/38) | **+2.6%** |
| **Table Questions (45)** | 82.2% (37/45) | **93.3%** (42/45) | <span style="color:green;font-weight:bold;">+11.1%</span> |
| **Diagram Questions (22)** | 86.4% (19/22) | **95.5%** (21/22) | <span style="color:green;font-weight:bold;">+9.1%</span> |
| **OVERALL ACCURACY (105)** | **83.8% (88/105)** | **91.4% (96/105)** | <span style="color:green;font-weight:bold;">+7.6% (96/105)</span> |

---

## 🏗️ Multi-Model Architecture & Hybrid Retrieval

```
32 Industrial Datasheet PDFs (MCUs, Sensors, Regulators, Motor Drivers, Op-Amps, Interfaces)
   │
   ├── Text Chunks (Layout-aware) ──────────────► Qdrant (multimodal_text)
   │
   ├── Tables (Markdown + Gemini 3.7 Summary) ──► Qdrant (multimodal_tables) ──┐
   │                                                                            │
   └── Diagrams (OpenCV Crop + BBox + OCR) ─────► Qdrant (multimodal_images) ──┤
                                                                               │
   User Query ──► [Dense Cosine Similarity] + [BM25 Lexical Keyword Search] ──┤
                                                                               ▼
                                                            Reciprocal Rank Fusion (RRF)
                                                                               │
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

### Multi-Model Subagent Squad Hierarchy
- **Executive CTO (Claude Opus 4.6)**: Query decomposition, cross-modality evidence validation, hallucination prevention, citation attribution (`[TEXT]`, `[TABLE: Page X]`, `[DIAGRAM: Page Y]`), and calibrated confidence refusal (< 0.35).
- **Vision Specialist Subagent (Gemini 3.7 Flash)**: Diagram extraction, schematic pinout mapping, and OpenCV bounding box validation.
- **Table Specialist Subagent (Gemini 3.7 Flash)**: `pdfplumber` multi-column table extraction, markdown formatting, and natural language semantic summarization.
- **Text Specialist Subagent (Gemini 3.7 Flash)**: Layout-aware document partitioning and recursive semantic chunking.
- **Hybrid Retrieval Engine**: Combines dense vector similarity with BM25 lexical keyword matching via Reciprocal Rank Fusion (RRF) for 100% precision on part numbers and register hex values.
- **Circuit Compatibility Engine**: Real-time I2C address collision detection, 3.3V vs 5.0V logic-level verification, and power budgeting.
- **Pin-to-Pin Wiring Assistant**: Generates exact wiring schedules with Mermaid.js visual bus diagrams.
- **Design Report Generator**: One-click publication-ready PDF Engineering Design Reports and Bill of Materials (BOM).

---

## 📦 Component Library (32 Industrial Datasheets)

1. **Microcontrollers & Wireless**: ESP32, Raspberry Pi RP2040, STM32F103, ATmega328P, nRF52840, ESP8266EX.
2. **Sensors & Converters**: BME280, DHT22, MPU6050, VL53L0X, DS18B20, INA219.
3. **Power Regulators & PMICs**: LM7805, LM317, AMS1117-3.3, TP4056, MP1584, XL6009.
4. **Motor Drivers & Actuators**: L298N, TB6612FNG, A4988, DRV8833, ULN2003A.
5. **Signal Conditioning & Op-Amps**: LM358, NE555, LM393, ADS1115, AD620.
6. **Communication & Interfaces**: MAX485, MCP2515, PCA9685, CH340G.

---

## ⚡ Quickstart

### 1. Local Python Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Generate 32 target datasheets & diagram crops
python3 -m src.ingest.download_datasheets

# Ingest into baseline & multimodal collections
python3 -m src.ingest.ingest_baseline
python3 -m src.ingest.ingest_multimodal

# Run 105-question benchmark
python3 -m src.eval.run_eval
```

### 2. Launch FastAPI Server & Streamlit Pro Studio
```bash
# Terminal 1: FastAPI Backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Streamlit Pro Studio
streamlit run frontend/app.py
```

### 3. Containerized One-Click Docker Setup
```bash
docker compose up -d --build
```
* **Streamlit Pro Studio**: `http://localhost:8501`
* **FastAPI Backend & Swagger**: `http://localhost:8000/docs`
* **Qdrant Vector Dashboard**: `http://localhost:6333/dashboard`

---

## 🧪 Unit Testing
```bash
pytest tests/ -v
# 10 passed in 1.13s (100%)
```
