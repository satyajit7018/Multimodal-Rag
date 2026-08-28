from fastapi import FastAPI
from pydantic import BaseModel

from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore
from src.retrieve.reranker import rerank
from src.generate.llm import answer_with_confidence

app = FastAPI(title="Datasheet Assistant API")

embedder = Embedder()
text_store = VectorStore(collection="multimodal_text")
table_store = VectorStore(collection="multimodal_tables")
image_store = VectorStore(collection="multimodal_images")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    source_table: str | None = None
    source_image: str | None = None


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    qvec = embedder.embed([req.question])[0]

    text_hits = text_store.search(qvec, top_k=3)
    table_hits = table_store.search(qvec, top_k=3)
    image_hits = image_store.search(qvec, top_k=3)

    all_hits = text_hits + table_hits + image_hits
    candidates = [h.payload.get("content", "") for h in all_hits]
    ranked = rerank(req.question, candidates, top_k=5)

    answer = answer_with_confidence(req.question, all_hits, ranked)

    source_table = next(
        (h.payload.get("content") for h in table_hits if h.score > 0.5), None
    )
    source_image = next(
        (h.payload.get("image_path") for h in image_hits if h.score > 0.5), None
    )

    return QueryResponse(answer=answer, source_table=source_table, source_image=source_image)


@app.get("/health")
def health():
    return {"status": "ok"}
