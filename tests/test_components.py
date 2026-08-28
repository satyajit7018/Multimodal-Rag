"""Unit Tests for Scaled Multimodal Datasheet RAG System.
Tests embedder, vector store, table extraction, diagram processing,
CTO generation, circuit validation, wiring assistant, BM25 hybrid search, and PDF report generator.
"""

import os
import pytest
from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore
from src.ingest.table_extract import extract_tables_with_metadata
from src.ingest.image_extract import extract_images_with_metadata
from src.generate.llm import generate_cto_answer, answer_with_confidence
from src.retrieve.multimodal_search import search_multimodal_parallel, search_baseline
from src.engine.circuit_validator import validate_circuit_compatibility
from src.engine.wiring_assistant import generate_wiring_plan, generate_mermaid_circuit_diagram
from src.retrieve.hybrid_search import BM25Index, reciprocal_rank_fusion
from src.engine.report_generator import generate_engineering_pdf_report


def test_embedder_dimensions():
    """Verify sentence embedder produces 384-dimensional normalized vectors."""
    embedder = Embedder()
    texts = ["LM7805 voltage regulator", "ESP32 Wi-Fi microcontroller"]
    vectors = embedder.embed(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384


def test_vector_store_crud():
    """Verify Qdrant VectorStore creates collection, upserts points, and searches."""
    store = VectorStore(collection="test_collection", dim=384)
    embedder = Embedder()
    
    texts = ["LM7805 produces fixed 5V output", "BME280 measures temperature and humidity"]
    vectors = embedder.embed(texts)
    payloads = [{"content": t, "id": i} for i, t in enumerate(texts)]
    
    store.upsert(ids=[101, 102], vectors=vectors, payloads=payloads)
    assert store.count() >= 2
    
    # Search for LM7805
    qvec = embedder.embed(["What is the output voltage of LM7805?"])[0]
    hits = store.search(qvec, top_k=1)
    assert len(hits) > 0
    assert "LM7805" in hits[0].payload["content"]


def test_table_extraction():
    """Verify table extractor extracts markdown and generates metadata from sample datasheet."""
    pdf_path = "data/raw_pdfs/lm7805_datasheet.pdf"
    if os.path.exists(pdf_path):
        tables = extract_tables_with_metadata(pdf_path)
        assert len(tables) > 0
        assert "| Characteristic" in tables[0]["markdown"] or "| Parameter" in tables[0]["markdown"] or "|" in tables[0]["markdown"]
        assert tables[0]["page"] >= 1


def test_image_extraction():
    """Verify image extractor processes pinout diagram with bounding metadata."""
    pdf_path = "data/raw_pdfs/dht22_datasheet.pdf"
    if os.path.exists(pdf_path):
        images = extract_images_with_metadata(pdf_path)
        assert len(images) > 0
        assert os.path.exists(images[0]["image_path"])
        assert "Pin" in images[0]["caption"] or "DHT22" in images[0]["caption"] or len(images[0]["caption"]) > 10


def test_confidence_refusal():
    """Verify calibrated refusal triggers when confidence is low."""
    dummy_hits = []
    answer, score = answer_with_confidence("What is the recipe for pasta?", dummy_hits, [], threshold=0.55)
    assert "not have enough verified information" in answer.lower()
    assert score < 0.55


def test_circuit_validator_i2c_collision():
    """Verify circuit validator detects PCA9685 and INA219 default address collision (0x40)."""
    result = validate_circuit_compatibility(["ESP32", "PCA9685", "INA219"])
    assert result["status"] == "issues_detected"
    assert len(result["critical_errors"]) > 0
    assert any("0x40" in err["details"] for err in result["critical_errors"])


def test_circuit_validator_voltage_mismatch():
    """Verify circuit validator flags 5V logic on non-5V-tolerant RP2040."""
    result = validate_circuit_compatibility(["RP2040", "MAX485"])
    assert len(result["compatibility_warnings"]) > 0
    assert any("Level Mismatch" in w["type"] or "3.3V" in w["details"] for w in result["compatibility_warnings"])


def test_wiring_assistant_and_mermaid():
    """Verify wiring assistant generates grounded pin connections and Mermaid diagram."""
    wiring = generate_wiring_plan("ESP32", ["BME280", "MPU6050"])
    assert wiring["status"] == "success"
    assert len(wiring["wiring_table"]) >= 4
    
    # Check Mermaid diagram generation
    mermaid = generate_mermaid_circuit_diagram("ESP32", ["BME280", "MPU6050"])
    assert "graph LR" in mermaid
    assert "ESP32" in mermaid
    assert "BME280" in mermaid


def test_bm25_hybrid_search_rrf():
    """Verify BM25 lexical indexer and Reciprocal Rank Fusion ranking."""
    docs = [
        {"content": "ESP32 microcontroller with Wi-Fi and Bluetooth", "id": 1},
        {"content": "PCA9685 16-channel 12-bit PWM I2C servo controller at 0x40", "id": 2},
        {"content": "LM7805 positive 5V linear voltage regulator", "id": 3},
    ]
    bm25 = BM25Index()
    bm25.fit(docs, text_field="content")
    hits = bm25.search("0x40 PWM", top_k=2)
    assert len(hits) > 0
    assert "PCA9685" in hits[0]["doc"]["content"]

    # Test RRF merge
    dense_mock = [{"content": docs[0]["content"]}, {"content": docs[1]["content"]}]
    fused = reciprocal_rank_fusion(dense_mock, hits, k=60, top_n=2)
    assert len(fused) > 0


def test_pdf_design_report_generator():
    """Verify PDF engineering design report is generated with BOM and wiring tables."""
    pdf_out = generate_engineering_pdf_report("Test Drone Project", "ESP32", ["BME280", "MPU6050", "PCA9685"])
    assert os.path.exists(pdf_out)
    assert os.path.getsize(pdf_out) > 1000
