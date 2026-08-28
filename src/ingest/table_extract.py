"""Table extraction. Converts extracted tables to markdown before embedding
so row/column relationships survive instead of being flattened into a
run-on sentence.
"""

import pdfplumber


def extract_tables(pdf_path: str) -> list[str]:
    tables_md = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                if not table or len(table) < 2:
                    continue
                header, *rows = table
                header = [str(h) if h is not None else "" for h in header]
                md = "| " + " | ".join(header) + " |\n"
                md += "|" + "---|" * len(header) + "\n"
                for row in rows:
                    row = [str(c) if c is not None else "" for c in row]
                    md += "| " + " | ".join(row) + " |\n"
                tables_md.append(md)
    return tables_md
