"""Cross-Encoder Reranker with Resilient Scoring Fallback.
Provides precision cross-attention relevance scoring for retrieved passages.
"""

import re
from typing import List

_RERANKER = None
_RERANKER_FAILED = False


def get_reranker():
    global _RERANKER, _RERANKER_FAILED
    if _RERANKER is None and not _RERANKER_FAILED:
        try:
            from sentence_transformers import CrossEncoder
            _RERANKER = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            print(f"[Warning] CrossEncoder load failed: {e}. Using lexical/semantic reranker.")
            _RERANKER_FAILED = True
    return _RERANKER


def _fallback_score(query: str, candidate: str) -> float:
    """Computes lexical token overlap and technical term matching score."""
    q_tokens = set(re.findall(r"[a-z0-9\-\.]+", query.lower()))
    c_tokens = set(re.findall(r"[a-z0-9\-\.]+", candidate.lower()))
    if not q_tokens:
        return 0.5
    overlap = len(q_tokens.intersection(c_tokens))
    score = overlap / len(q_tokens)
    # Give slight bonus for exact phrase/number containment
    for tok in q_tokens:
        if len(tok) >= 3 and tok in candidate.lower():
            score += 0.15
    return min(score, 1.0)


def rerank(query: str, candidates: List[str], top_k: int = 5) -> List[str]:
    """Reranks candidate strings by relevance to the query."""
    if not candidates:
        return []
    if len(candidates) <= 1:
        return candidates[:top_k]

    model = get_reranker()
    if model is not None:
        try:
            scores = model.predict([(query, c) for c in candidates], show_progress_bar=False)
            ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
            return [c for c, _ in ranked[:top_k]]
        except Exception:
            pass

    # Resilient fallback scoring
    scored = [(c, _fallback_score(query, c)) for c in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:top_k]]
