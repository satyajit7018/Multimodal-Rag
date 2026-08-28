# Multimodal Datasheet RAG — Detailed Build Plan

Goal: prove that extracting tables and diagrams separately beats plain text
chunking on a real electronics datasheet corpus, with a measured comparison,
a working demo, and a deployed API.

## Repo structure

```
datasheet-rag/
├── data/
│   ├── raw_pdfs/              # source datasheets
│   ├── eval_set.json          # your 40 hand-written Q&A pairs
│   └── extracted/             # cached extraction output
├── src/
│   ├── ingest/
│   │   ├── extract.py         # unstructured element classification
│   │   ├── table_extract.py   # pdfplumber/camelot table pulling
│   │   └── image_extract.py   # figure crop + OCR + caption
│   ├── embed/
│   │   └── embedder.py        # sentence-transformers wrapper
│   ├── retrieve/
│   │   ├── vector_store.py    # Qdrant collections + query
│   │   └── reranker.py        # cross-encoder rerank
│   ├── generate/
│   │   └── llm.py             # prompt + answer generation
│   ├── eval/
│   │   └── run_eval.py        # baseline vs multimodal scoring
│   └── api/
│       └── main.py            # FastAPI app
├── frontend/
│   └── app.py                 # Streamlit demo
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Environment setup (do this before Day 1)

`requirements.txt`:
```
fastapi
uvicorn
qdrant-client
sentence-transformers
unstructured[pdf]
pdfplumber
camelot-py[cv]
easyocr
opencv-python
langchain
langchain-text-splitters
anthropic
streamlit
pydantic
python-dotenv
```

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker run -p 6333:6333 qdrant/qdrant   # local Qdrant instance
```

---

## Week 1: Baseline and corpus

**Day 1-2 — Corpus**
Collect 15-20 datasheets: ESP32, a common temperature sensor (DHT22 or
BME280), an op-amp (LM358), a voltage regulator (LM7805), an H-bridge
driver. Put PDFs in `data/raw_pdfs/`. Mix of dense-table datasheets and
diagram-heavy ones on purpose, you want both failure modes represented.

**Day 3-5 — Baseline text-only pipeline**

`src/ingest/extract.py` (naive text version for the baseline):
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap
    )
    return splitter.split_text(text)
```

`src/embed/embedder.py`:
```python
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]):
        return self.model.encode(texts, normalize_embeddings=True).tolist()
```

`src/retrieve/vector_store.py`:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class VectorStore:
    def __init__(self, collection="baseline_text", dim=384, host="localhost"):
        self.client = QdrantClient(host=host, port=6333)
        self.collection = collection
        if not self.client.collection_exists(collection):
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vectors, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector, top_k=5):
        return self.client.search(
            collection_name=self.collection, query_vector=query_vector, limit=top_k
        )
```

Wire these three together in a small script that reads every PDF, chunks it,
embeds the chunks, and upserts into the `baseline_text` collection.

**Day 6-7 — Eval set**

Write it now, before extraction gets more complex, so it stays honest.
`data/eval_set.json`:
```json
[
  {
    "id": "t1",
    "category": "text",
    "question": "What is the ESP32 used for in typical IoT applications?",
    "answer": "Wi-Fi and Bluetooth enabled microcontroller for IoT connectivity",
    "source_doc": "esp32_datasheet.pdf"
  },
  {
    "id": "tab1",
    "category": "table",
    "question": "What is the operating voltage range for the LM7805?",
    "answer": "7V to 25V input, 5V regulated output",
    "source_doc": "lm7805_datasheet.pdf"
  },
  {
    "id": "img1",
    "category": "diagram",
    "question": "Which pin on the DHT22 is the data output pin?",
    "answer": "Pin 2",
    "source_doc": "dht22_datasheet.pdf"
  }
]
```
Write 15 of category `text`, 15 `table`, 10 `diagram`. Run the baseline
pipeline against all 40, score by exact-match or manual grading, record the
per-category accuracy. This number becomes the "before" row in your final
comparison table.

Milestone: baseline RAG working, eval scored, table and diagram accuracy
visibly weaker than text accuracy.

---

## Week 2: Multimodal extraction

**Day 8-9 — Layout-aware extraction**

`src/ingest/extract.py` (add the multimodal version alongside the baseline):
```python
from unstructured.partition.pdf import partition_pdf

def extract_elements(pdf_path: str):
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        infer_table_structure=True,
    )
    text_els, table_els, image_els = [], [], []
    for el in elements:
        kind = el.category
        if kind == "Table":
            table_els.append(el)
        elif kind in ("Image", "Figure"):
            image_els.append(el)
        else:
            text_els.append(el)
    return text_els, table_els, image_els
```

**Day 10-11 — Table extraction**

`unstructured` handles simple tables reasonably but dense multi-column specs
often come out cleaner through `pdfplumber`:
```python
import pdfplumber

def extract_tables(pdf_path: str):
    tables_md = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                header, *rows = table
                md = "| " + " | ".join(str(h) for h in header) + " |\n"
                md += "|" + "---|" * len(header) + "\n"
                for row in rows:
                    md += "| " + " | ".join(str(c) for c in row) + " |\n"
                tables_md.append(md)
    return tables_md
```
Converting to markdown before embedding keeps row/column relationships
intact instead of flattening a table into a run-on sentence.

**Day 12-14 — Image and diagram handling**

`src/ingest/image_extract.py`:
```python
import cv2
import easyocr

reader = easyocr.Reader(["en"])

def preprocess_diagram(image_path: str):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return img, contours

def ocr_diagram(image_path: str) -> str:
    results = reader.readtext(image_path, detail=0)
    return " ".join(results)
```
For captions, send the cropped figure to a vision model:
```python
import anthropic

client = anthropic.Anthropic()

def caption_figure(image_bytes: bytes) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_bytes}},
                {"type": "text", "text": "Describe this electronics diagram, including any labeled pins or values."}
            ]
        }]
    )
    return response.content[0].text
```
Embed both the OCR text and the caption for each figure. This is where your
OpenCV background from the brain tumor project carries over directly, same
idea of isolating meaningful regions before downstream processing.

Milestone: every PDF produces three parallel outputs, text chunks, markdown
tables, and image caption+OCR pairs, all ready to embed.

---

## Week 3: Retrieval, generation, and the comparison

**Day 15-16 — Three collections, parallel query**

Create `multimodal_text`, `multimodal_tables`, `multimodal_images` as
separate Qdrant collections using the same `VectorStore` class from Week 1.
Query all three per question:
```python
def multimodal_search(query: str, embedder, stores: dict, top_k=3):
    qvec = embedder.embed([query])[0]
    results = {}
    for name, store in stores.items():
        results[name] = store.search(qvec, top_k=top_k)
    return results
```

Rerank the merged results with a cross-encoder:
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, candidates: list[str], top_k=5):
    scores = reranker.predict([(query, c) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [c for c, s in ranked[:top_k]]
```

**Day 17 — Generation prompt**
```python
SYSTEM_PROMPT = """You answer questions using only the provided context.
If a table is provided, prefer exact values from it over descriptions in
surrounding text. Cite whether each part of your answer came from text,
a table, or a diagram. If the context does not contain enough information,
say so explicitly rather than guessing."""
```

**Day 18-19 — Run the comparison**

Run `data/eval_set.json` against both the Week 1 baseline collection and
the new multimodal collections. Build the table that becomes your headline
result:

| Category | Baseline (text-only) | Multimodal |
|---|---|---|
| Text questions | ~85% | ~88% |
| Table questions | ~35% | ~90% |
| Diagram questions | ~10% | ~75% |

(numbers above are illustrative, yours will come from the actual run)

**Day 20-21 — Confidence threshold**

```python
CONFIDENCE_THRESHOLD = 0.55

def answer_with_confidence(query, search_results, embedder, llm_fn):
    top_score = max(r.score for r in search_results) if search_results else 0
    if top_score < CONFIDENCE_THRESHOLD:
        return "I don't have enough information in the provided documents to answer this confidently."
    return llm_fn(query, search_results)
```
Log how often this triggers across the eval set, that number is worth
reporting too.

Milestone: a documented, numbers-backed table proving multimodal extraction
fixes the specific failure mode plain RAG has.

---

## Week 4: Frontend, grounding, deployment

**Day 22-23 — Streamlit frontend**

`frontend/app.py`:
```python
import streamlit as st
import requests

st.title("Datasheet Assistant")
uploaded = st.file_uploader("Upload a datasheet", type="pdf")
question = st.text_input("Ask a question")

if st.button("Ask") and question:
    resp = requests.post("http://localhost:8000/query", json={"question": question})
    data = resp.json()
    st.write(data["answer"])
    if data.get("source_image"):
        st.image(data["source_image"], caption="Source region")
    if data.get("source_table"):
        st.markdown(data["source_table"])
```

**Day 24-25 — Source grounding**

Track a bounding box alongside each extracted image/table element during
ingestion, store it in the Qdrant payload, and return the cropped region
(or the markdown table) alongside the answer so the frontend can display
exactly what the system used.

**Day 26 — Feedback logging**
```python
import json, datetime

def log_feedback(question, answer, is_correct: bool):
    entry = {"question": question, "answer": answer, "correct": is_correct,
              "timestamp": datetime.datetime.utcnow().isoformat()}
    with open("data/feedback_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**Day 27-28 — Docker, CI/CD, deployment**

`Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml`:
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - qdrant
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
```

Basic GitHub Actions redeploy workflow, `.github/workflows/deploy.yml`:
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to EC2
        run: |
          ssh ${{ secrets.EC2_HOST }} "cd datasheet-rag && git pull && docker compose up -d --build"
```

Deploy on an AWS EC2 free-tier instance or Lightsail. Write the README with
your architecture diagram and the baseline-vs-multimodal comparison table
placed near the top, then record a 60-90 second demo clip showing a table
question and a diagram question both answered correctly with the source
highlighted.

---

## Resume bullet template

"Built a multimodal RAG system over electronics datasheets that extracts
and separately indexes text, tables, and diagrams (unstructured,
pdfplumber, OpenCV, EasyOCR); measured a [X]% to [Y]% accuracy improvement
on table and diagram questions over a text-only baseline; deployed on AWS
with Docker and CI/CD."

## Interview talking points to have ready

- Why plain RAG fails on structured content, and how you proved it with the baseline comparison
- Why you kept text, tables, and images in separate collections instead of one merged space, and the tradeoff (more infra, more control over per-source weighting)
- What the confidence threshold does and why silent failure is a known RAG problem
- What you'd add next if given more time (the ColPali-style visual embedding comparison is a good answer here, it shows research awareness without you having had to build it)
