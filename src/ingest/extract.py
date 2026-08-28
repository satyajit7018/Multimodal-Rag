"""Extraction utilities.

extract_text_baseline() is the naive, text-only path used for the Week 1
baseline pipeline. extract_elements() is the layout-aware, multimodal path
added in Week 2 that separates text, tables, and images.
"""

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
    from unstructured.partition.pdf import partition_pdf

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
