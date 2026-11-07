
import hashlib
from pathlib import Path
from pypdf import PdfReader

from src.models import ExtractedPdfPage

"""generate hash value of the pdf"""
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        # b"":empty byte sequence. File reaches its end; iteration stops
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def document_id_from_hash(content_hash: str) -> str:
    """Create a stable, non-PHI identifier for this exact document version."""
    return f"pdf-{content_hash[:16]}"


def extract_pdf_pages(
    pdf_path: Path,
    document_id: str,
    relative_path: str,
) -> list[ExtractedPdfPage]:
    """Extract text from each page of a text-based PDF.

    A page with no extractable text is kept as an empty page record. That makes
    a later OCR requirement visible instead of silently losing source pages.
    """
    reader = PdfReader(pdf_path)
    return [
        ExtractedPdfPage(
            document_id=document_id,
            relative_path=relative_path,
            page_number=page_number,
            text=page.extract_text() or "",
        )
        for page_number, page in enumerate(reader.pages, start=1)
    ]

