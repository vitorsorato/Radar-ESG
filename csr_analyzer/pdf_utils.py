from typing import Optional

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None) -> str:
    """Extract text from a PDF file.

    Args:
        pdf_path: Path to a PDF file on disk.
        max_pages: Optional page limit to stop early.

    Returns:
        Full text extracted from the PDF, or empty string if extraction fails.
    """
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        text_chunks = []
        limit = num_pages if max_pages is None else min(num_pages, max_pages)
        for page_index in range(limit):
            page = reader.pages[page_index]
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
        return "\n\n".join(text_chunks)
    except Exception:
        return ""
