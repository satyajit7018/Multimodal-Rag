"""Extraction utilities.

extract_text_baseline() is the naive, text-only path used for baseline comparisons.
extract_elements() is the layout-aware path that separates text, tables, and images.
"""

from __future__ import annotations
import importlib
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_baseline(pdf_path: str) -> str:
    """Pull raw text from every page, no layout awareness."""
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap
    )
    return splitter.split_text(text)


def extract_elements(pdf_path: str):
    """Layout-aware extraction: classifies each PDF element as text,
    table, or image so they can be processed and embedded separately.
    """
    try:
        unstructured_pdf = importlib.import_module("unstructured.partition.pdf")
        partition_pdf = getattr(unstructured_pdf, "partition_pdf")

        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",
            extract_images_in_pdf=True,
            infer_table_structure=True,
        )

        text_els, table_els, image_els = [], [], []
        for el in elements:
            kind = getattr(el, "category", "")
            if kind == "Table":
                table_els.append(el)
            elif kind in ("Image", "Figure"):
                image_els.append(el)
            else:
                text_els.append(el)

        return text_els, table_els, image_els
    except Exception:
        # Fallback to pdfplumber/pypdf extraction if unstructured is not installed
        from src.ingest.table_extract import extract_tables_with_metadata
        from src.ingest.image_extract import extract_images_with_metadata
        
        tables = extract_tables_with_metadata(pdf_path)
        images = extract_images_with_metadata(pdf_path)
        text = extract_text_baseline(pdf_path)
        return [text], tables, images
