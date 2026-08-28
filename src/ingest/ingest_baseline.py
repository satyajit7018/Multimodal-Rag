"""Baseline Text-Only Ingestion Runner.
Naively extracts text from all PDF datasheets in data/raw_pdfs/,
chunks them into fixed-size windows without layout awareness,
embeds them, and indexes them into the 'baseline_text' Qdrant collection.
"""

import os
import glob
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore

RAW_PDF_DIR = "data/raw_pdfs"


def run_baseline_ingestion(pdf_dir: str = RAW_PDF_DIR) -> int:
    """Ingests all PDFs into the baseline_text collection."""
    print("=" * 60)
    print("STARTING BASELINE TEXT-ONLY INGESTION")
    print("=" * 60)

    pdf_files = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    if not pdf_files:
        print(f"No PDFs found in {pdf_dir}. Please run download_datasheets.py first.")
        return 0

    embedder = Embedder()
    store = VectorStore(collection="baseline_text")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    all_chunks = []
    all_payloads = []
    point_id = 1

    for pdf_path in pdf_files:
        pdf_name = os.path.basename(pdf_path)
        print(f"Processing baseline text: {pdf_name}...")
        reader = PdfReader(pdf_path)

        for page_idx, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if not page_text.strip():
                continue

            chunks = splitter.split_text(page_text)
            for chunk in chunks:
                all_chunks.append(chunk)
                all_payloads.append({
                    "content": chunk,
                    "doc_name": pdf_name,
                    "page": page_idx,
                    "type": "text_baseline",
                })

    print(f"Total chunks extracted: {len(all_chunks)}. Computing embeddings...")
    vectors = embedder.embed(all_chunks)
    ids = list(range(1, len(all_chunks) + 1))

    print(f"Indexing {len(ids)} vectors into Qdrant collection 'baseline_text'...")
    store.upsert(ids=ids, vectors=vectors, payloads=all_payloads)

    print(f"Baseline ingestion complete! Total points indexed: {store.count()}")
    return len(ids)


if __name__ == "__main__":
    run_baseline_ingestion()
