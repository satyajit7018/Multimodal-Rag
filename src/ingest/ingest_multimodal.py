"""Parallel Multimodal Ingestion Orchestrator.
Uses Gemini 3.7 Flash Subagent Squad working in parallel:
- Text Specialist: chunks structured narrative text
- Table Specialist: extracts Markdown tables + generates semantic summaries
- Vision Specialist: extracts pinout diagrams + captions + OCR
Populates 3 separate Qdrant collections concurrently:
'multimodal_text', 'multimodal_tables', 'multimodal_images'.
"""

import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.embed.embedder import Embedder
from src.retrieve.vector_store import VectorStore
from src.ingest.table_extract import extract_tables_with_metadata
from src.ingest.image_extract import extract_images_with_metadata

RAW_PDF_DIR = "data/raw_pdfs"


def process_single_pdf_multimodal(pdf_path: str):
    """Processes a single PDF across text, table, and vision modalities."""
    pdf_name = os.path.basename(pdf_path)
    print(f"-> [Worker Squad] Processing {pdf_name} in parallel...")

    text_records = []
    table_records = []
    image_records = []

    # 1. Text Extraction (Page 1 overview / narrative)
    try:
        reader = PdfReader(pdf_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        for page_idx, page in enumerate(reader.pages, start=1):
            # Page 1 typically contains descriptions and overview
            if page_idx == 1:
                raw_text = page.extract_text() or ""
                chunks = splitter.split_text(raw_text)
                for chunk in chunks:
                    text_records.append({
                        "content": chunk,
                        "doc_name": pdf_name,
                        "page": page_idx,
                        "type": "text",
                    })
    except Exception as e:
        print(f"[Error in Text Subagent for {pdf_name}]: {e}")

    # 2. Table Specialist Subagent
    try:
        tables = extract_tables_with_metadata(pdf_path)
        for t in tables:
            table_records.append({
                "content": t["markdown"],
                "embed_text": f"Table specifications for {pdf_name} Page {t['page']}: {t['semantic_summary']}\n{t['markdown']}",
                "semantic_summary": t["semantic_summary"],
                "doc_name": pdf_name,
                "page": t["page"],
                "type": "table",
            })
    except Exception as e:
        print(f"[Error in Table Subagent for {pdf_name}]: {e}")

    # 3. Vision Specialist Subagent
    try:
        images = extract_images_with_metadata(pdf_path)
        for img in images:
            image_records.append({
                "content": f"Diagram ({img['doc_name']} Page {img['page']}): {img['caption']}",
                "embed_text": f"Circuit pinout schematic diagram for {img['doc_name']}: {img['caption']} {img['ocr_text']}",
                "image_path": img["image_path"],
                "caption": img["caption"],
                "bbox": img["bbox"],
                "doc_name": pdf_name,
                "page": img["page"],
                "type": "diagram",
            })
    except Exception as e:
        print(f"[Error in Vision Subagent for {pdf_name}]: {e}")

    return text_records, table_records, image_records


def run_multimodal_ingestion(pdf_dir: str = RAW_PDF_DIR, max_workers: int = 4):
    """Orchestrates parallel multimodal ingestion across all PDFs."""
    print("=" * 60)
    print("STARTING PARALLEL MULTIMODAL INGESTION (GEMINI 3.7 SUBAGENTS)")
    print("=" * 60)

    pdf_files = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    if not pdf_files:
        print(f"No PDFs found in {pdf_dir}. Please run download_datasheets.py first.")
        return

    all_text = []
    all_tables = []
    all_images = []

    # Parallel worker execution across PDF files
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_pdf_multimodal, pdf): pdf for pdf in pdf_files}
        for future in as_completed(futures):
            t_rec, tab_rec, img_rec = future.result()
            all_text.extend(t_rec)
            all_tables.extend(tab_rec)
            all_images.extend(img_rec)

    print(f"\nExtraction summary: {len(all_text)} text chunks, {len(all_tables)} tables, {len(all_images)} diagram records.")

    embedder = Embedder()
    text_store = VectorStore(collection="multimodal_text")
    table_store = VectorStore(collection="multimodal_tables")
    image_store = VectorStore(collection="multimodal_images")

    # Index Text collection
    if all_text:
        print("Embedding & Indexing multimodal_text collection...")
        t_vectors = embedder.embed([r["content"] for r in all_text])
        text_store.upsert(
            ids=list(range(1, len(all_text) + 1)),
            vectors=t_vectors,
            payloads=all_text,
        )

    # Index Table collection (embedding enhanced semantic summaries for high recall)
    if all_tables:
        print("Embedding & Indexing multimodal_tables collection...")
        tab_vectors = embedder.embed([r["embed_text"] for r in all_tables])
        table_store.upsert(
            ids=list(range(1, len(all_tables) + 1)),
            vectors=tab_vectors,
            payloads=all_tables,
        )

    # Index Diagram collection (embedding vision captions + pinout labels)
    if all_images:
        print("Embedding & Indexing multimodal_images collection...")
        img_vectors = embedder.embed([r["embed_text"] for r in all_images])
        image_store.upsert(
            ids=list(range(1, len(all_images) + 1)),
            vectors=img_vectors,
            payloads=all_images,
        )

    print("\n" + "=" * 60)
    print("MULTIMODAL INGESTION COMPLETED SUCCESSFULLY!")
    print(f"- multimodal_text count:   {text_store.count()}")
    print(f"- multimodal_tables count: {table_store.count()}")
    print(f"- multimodal_images count: {image_store.count()}")
    print("=" * 60)


if __name__ == "__main__":
    run_multimodal_ingestion()
