"""Parallel Multi-Store Retrieval & Cross-Encoder Reranking Engine.
Queries 'multimodal_text', 'multimodal_tables', and 'multimodal_images' collections
in parallel using ThreadPoolExecutor, aggregates candidate hits, and executes
cross-encoder precision reranking.
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore
from src.retrieve.reranker import rerank

_EMBEDDER = None
_TEXT_STORE = None
_TABLE_STORE = None
_IMAGE_STORE = None
_BASELINE_STORE = None


def get_components():
    global _EMBEDDER, _TEXT_STORE, _TABLE_STORE, _IMAGE_STORE, _BASELINE_STORE
    if _EMBEDDER is None:
        _EMBEDDER = Embedder()
        _TEXT_STORE = VectorStore(collection="multimodal_text")
        _TABLE_STORE = VectorStore(collection="multimodal_tables")
        _IMAGE_STORE = VectorStore(collection="multimodal_images")
        _BASELINE_STORE = VectorStore(collection="baseline_text")
    return _EMBEDDER, _TEXT_STORE, _TABLE_STORE, _IMAGE_STORE, _BASELINE_STORE


def search_baseline(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieves candidates from the naive text-only baseline collection."""
    embedder, _, _, _, baseline_store = get_components()
    qvec = embedder.embed([question])[0]
    hits = baseline_store.search(qvec, top_k=top_k, query_text=question)
    
    results = []
    for h in hits:
        results.append({
            "content": h.payload.get("content", ""),
            "score": h.score,
            "doc_name": h.payload.get("doc_name", ""),
            "page": h.payload.get("page", 1),
            "type": "text_baseline",
        })
    return results


def search_multimodal_parallel(question: str, top_k_per_modality: int = 3, top_rerank: int = 5) -> Dict[str, Any]:
    """Queries all 3 multimodal collections concurrently and performs cross-encoder reranking."""
    embedder, text_store, table_store, image_store, _ = get_components()
    qvec = embedder.embed([question])[0]

    # Parallel query across 3 stores
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_text = executor.submit(text_store.search, qvec, top_k_per_modality, question)
        f_table = executor.submit(table_store.search, qvec, top_k_per_modality, question)
        f_image = executor.submit(image_store.search, qvec, top_k_per_modality, question)

        text_hits = f_text.result()
        table_hits = f_table.result()
        image_hits = f_image.result()

    all_hits = list(text_hits) + list(table_hits) + list(image_hits)
    
    # Candidate text passages for reranking
    candidates = []
    hit_map = {}
    for h in all_hits:
        content = h.payload.get("content") or h.payload.get("embed_text") or h.payload.get("caption", "")
        if content and content not in hit_map:
            candidates.append(content)
            hit_map[content] = h

    # Cross-encoder precision rerank
    ranked_content = rerank(question, candidates, top_k=top_rerank) if candidates else []

    # If an image hit is relevant, ensure its diagram pins and caption are grounded in contexts
    if image_hits and image_hits[0].score > 0.28:
        top_img_content = image_hits[0].payload.get("content") or image_hits[0].payload.get("embed_text") or image_hits[0].payload.get("caption")
        if top_img_content and top_img_content not in ranked_content:
            ranked_content.append(top_img_content)

    # Identify primary source table & diagram for visual grounding
    source_table = None
    source_table_meta = None
    for h in sorted(table_hits, key=lambda x: x.score, reverse=True):
        if h.score > 0.35:
            source_table = h.payload.get("content")
            source_table_meta = {
                "doc_name": h.payload.get("doc_name"),
                "page": h.payload.get("page"),
                "summary": h.payload.get("semantic_summary"),
            }
            break

    source_image = None
    source_image_meta = None
    for h in sorted(image_hits, key=lambda x: x.score, reverse=True):
        if h.score > 0.35:
            source_image = h.payload.get("image_path")
            source_image_meta = {
                "doc_name": h.payload.get("doc_name"),
                "page": h.payload.get("page"),
                "caption": h.payload.get("caption"),
                "bbox": h.payload.get("bbox"),
            }
            break

    return {
        "all_hits": all_hits,
        "ranked_contexts": ranked_content,
        "source_table": source_table,
        "source_table_meta": source_table_meta,
        "source_image": source_image,
        "source_image_meta": source_image_meta,
        "text_hits": text_hits,
        "table_hits": table_hits,
        "image_hits": image_hits,
    }
