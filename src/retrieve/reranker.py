from sentence_transformers import CrossEncoder

_reranker = None


def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank(query: str, candidates: list[str], top_k: int = 5) -> list[str]:
    model = get_reranker()
    scores = model.predict([(query, c) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:top_k]]
