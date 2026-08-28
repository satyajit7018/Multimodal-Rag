import anthropic

SYSTEM_PROMPT = """You answer questions using only the provided context.
If a table is provided, prefer exact values from it over descriptions in
surrounding text. Cite whether each part of your answer came from text,
a table, or a diagram. If the context does not contain enough information,
say so explicitly rather than guessing."""

CONFIDENCE_THRESHOLD = 0.55

_client = None


def get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    response = get_client().messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            }
        ],
    )
    return response.content[0].text


def answer_with_confidence(question: str, search_results, context_chunks: list[str]) -> str:
    top_score = max((r.score for r in search_results), default=0)
    if top_score < CONFIDENCE_THRESHOLD:
        return "I don't have enough information in the provided documents to answer this confidently."
    return generate_answer(question, context_chunks)
