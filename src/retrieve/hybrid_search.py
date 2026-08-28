"""Hybrid Search Engine (Dense Vector + BM25 Lexical Matching).
Combines dense semantic vector embeddings with BM25 keyword matching
using Reciprocal Rank Fusion (RRF) for high precision on part numbers,
hex registers, pin codes, and tolerances.
"""

from __future__ import annotations
import re
import math
from collections import Counter
from typing import List, Dict, Any


class BM25Index:
    """Lightweight in-memory BM25 lexical indexer for electronics datasheets."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[Dict[str, Any]] = []
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.df: Dict[str, int] = Counter()
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes text preserving hex (0x40), units (3.3v, 16mhz), and part numbers."""
        return re.findall(r"[a-zA-Z0-9_\-\.\+\/]+", text.lower())

    def fit(self, documents: List[Dict[str, Any]], text_field: str = "content"):
        """Indexes documents and calculates term frequencies and inverse document frequencies."""
        self.corpus = documents
        self.doc_len = []
        self.df = Counter()
        total_len = 0

        for doc in documents:
            text = doc.get(text_field, "")
            tokens = set(self._tokenize(text))
            for t in tokens:
                self.df[t] += 1
            length = len(self._tokenize(text))
            self.doc_len.append(length)
            total_len += length

        n_docs = max(len(documents), 1)
        self.avg_doc_len = total_len / n_docs if n_docs > 0 else 1.0

        for term, freq in self.df.items():
            # Standard Lucene/BM25 IDF formula
            self.idf[term] = math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 5, text_field: str = "content") -> List[Dict[str, Any]]:
        """Scores and returns top-k matching documents using BM25."""
        q_tokens = self._tokenize(query)
        scores = []

        for idx, doc in enumerate(self.corpus):
            doc_tokens = self._tokenize(doc.get(text_field, ""))
            tf = Counter(doc_tokens)
            d_len = self.doc_len[idx] if idx < len(self.doc_len) else len(doc_tokens)
            score = 0.0

            for t in q_tokens:
                if t in tf:
                    t_idf = self.idf.get(t, 0.1)
                    t_tf = tf[t]
                    denom = t_tf + self.k1 * (1 - self.b + self.b * (d_len / max(self.avg_doc_len, 1.0)))
                    score += t_idf * (t_tf * (self.k1 + 1)) / max(denom, 1e-6)

            scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [{"score": s, "doc": d} for s, d in scores[:top_k] if s > 0]


def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]],
    sparse_results: List[Dict[str, Any]],
    k: int = 60,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """Merges dense vector ranking with BM25 lexical ranking using Reciprocal Rank Fusion (RRF).
    RRF_score(d) = sum(1 / (k + rank_i(d)))
    """
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    # Dense ranks
    for rank, item in enumerate(dense_results, start=1):
        content = item.get("content") or item.get("embed_text") or str(item)
        doc_map[content] = item
        rrf_scores[content] = rrf_scores.get(content, 0.0) + (1.0 / (k + rank))

    # Sparse / BM25 ranks
    for rank, item in enumerate(sparse_results, start=1):
        doc = item.get("doc", {})
        content = doc.get("content") or doc.get("embed_text") or str(doc)
        if content not in doc_map:
            doc_map[content] = doc
        rrf_scores[content] = rrf_scores.get(content, 0.0) + (1.0 / (k + rank))

    # Sort fused results by RRF score
    fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for content, score in fused[:top_n]:
        res_item = doc_map[content].copy()
        res_item["rrf_score"] = round(score, 4)
        results.append(res_item)

    return results
