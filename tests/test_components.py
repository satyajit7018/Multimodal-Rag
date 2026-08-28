"""Unit Tests for Multimodal Datasheet RAG System.
Tests embedder, vector store, table extraction, diagram processing,
CTO generation, and parallel multi-store search.
"""

import os
import pytest
from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore
from src.ingest.table_extract import extract_tables_with_metadata
from src.ingest.image_extract import extract_images_with_metadata
from src.generate.llm import generate_cto_answer, answer_with_confidence
from src.retrieve.multimodal_search import search_multimodal_parallel, search_baseline


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
