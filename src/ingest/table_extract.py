"""Table Extraction Specialist Subagent (Gemini 3.7 Flash + pdfplumber).
Extracts multi-column tables, converts to clean Markdown tables, generates
natural language semantic summaries for dense vector indexing, and tracks page metadata.
"""

import pdfplumber
from src.generate.providers import MultiModelSquad


def extract_tables_with_metadata(pdf_path: str) -> list[dict]:
    """Extracts tables from a PDF with bounding boxes, markdown representation,
    and semantic summaries generated for enhanced vector search recall.
    """
    extracted_tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if not tables:
                    continue

                for table_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue

                    # Clean header & rows
                    raw_header = table[0]
                    header = [str(h).strip().replace("\n", " ") if h is not None else "" for h in raw_header]
                    
                    rows = []
                    for raw_row in table[1:]:
                        clean_row = [str(c).strip().replace("\n", " ") if c is not None else "" for c in raw_row]
                        # Skip completely empty rows
                        if any(clean_row):
                            rows.append(clean_row)

                    if not rows:
                        continue

                    # Construct clean Markdown table
                    md = "| " + " | ".join(header) + " |\n"
                    md += "|" + "---|" * len(header) + "\n"
                    for row in rows:
                        # Pad row if shorter than header
                        while len(row) < len(header):
                            row.append("")
                        md += "| " + " | ".join(row[:len(header)]) + " |\n"

                    # Generate semantic summary via Gemini 3.7 Flash Subagent
                    table_title = f"Page {page_idx} Table {table_idx + 1}"
                    semantic_summary = MultiModelSquad.table_subagent_summarize(md, title=table_title)

                    extracted_tables.append({
                        "markdown": md,
                        "semantic_summary": semantic_summary,
                        "page": page_idx,
                        "table_index": table_idx + 1,
                        "num_rows": len(rows),
                        "num_cols": len(header),
                    })
    except Exception as e:
        print(f"Error extracting tables from {pdf_path}: {e}")

    return extracted_tables


def extract_tables(pdf_path: str) -> list[str]:
    """Backward-compatible helper returning list of markdown strings."""
    tables_meta = extract_tables_with_metadata(pdf_path)
    return [t["markdown"] for t in tables_meta]
