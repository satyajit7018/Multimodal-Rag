"""CTO Executive Generation & Guardrail Layer (Claude Opus 4.6).
Oversees cross-modality synthesis, enforces grounded citations ([TEXT], [TABLE: Page X], [DIAGRAM: Page Y]),
and applies confidence gating to prevent hallucinations.
"""

from typing import List, Tuple, Optional
from src.generate.providers import MultiModelSquad

CTO_SYSTEM_PROMPT = """You are the Executive CTO of the Datasheet Assistant RAG system.
You answer user engineering questions strictly using only the provided context snippets.

Rules:
1. Grounding & Accuracy: If numerical limits, operating ratings, or pin configurations are asked, quote exact values and units from the provided tables or diagrams.
2. Citations: Explicitly cite where each piece of information came from:
   - Use [TEXT: <Doc> Page <N>] for prose descriptions.
   - Use [TABLE: <Doc> Page <N>] for electrical ratings/tables.
   - Use [DIAGRAM: <Doc> Page <N>] for pinouts, schematics, and wiring.
3. Conflict Resolution: If text and table disagree, always trust the exact numerical table specification.
4. Calibrated Refusal: If the provided context does NOT contain sufficient information to answer the question accurately, politely refuse rather than speculating or guessing. State: "I do not have enough verified information in the provided datasheets to answer this question confidently."
"""

CONFIDENCE_THRESHOLD = 0.35


def generate_cto_answer(question: str, context_chunks: List[str]) -> str:
    """Invokes Claude Opus 4.6 (with fallback) to synthesize a grounded answer."""
    context_str = "\n\n---\n\n".join(context_chunks)
    user_prompt = f"Technical Context:\n{context_str}\n\nUser Question:\n{question}\n\nCTO Synthesized Answer:"
    
    return MultiModelSquad.cto_generate(
        system_prompt=CTO_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model="claude-3-7-sonnet-20250219",
        max_tokens=600,
        temperature=0.1,
    )


def answer_with_confidence(
    question: str,
    search_results: list,
    context_chunks: List[str],
    threshold: float = CONFIDENCE_THRESHOLD,
) -> Tuple[str, float]:
    """Applies confidence gating. Refuses if top retrieval relevance score < threshold."""
    top_score = 0.0
    if search_results:
        scores = []
        for r in search_results:
            if isinstance(r, dict):
                scores.append(r.get("score", 0.0))
            else:
                scores.append(getattr(r, "score", 0.0))
        top_score = max(scores, default=0.0)

    if top_score < threshold:
        refusal_msg = (
            "I do not have enough verified information in the provided datasheets to answer this question confidently. "
            f"(Confidence score {top_score:.2f} is below the threshold of {threshold:.2f})."
        )
        return refusal_msg, top_score

    answer = generate_cto_answer(question, context_chunks)
    return answer, top_score


def generate_answer(question: str, context_chunks: List[str]) -> str:
    """Backward compatibility wrapper."""
    return generate_cto_answer(question, context_chunks)
