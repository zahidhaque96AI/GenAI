
"""Incrementally ingest PDFs while preserving file and page provenance."""

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from src.models import ExtractedPdfPage, PdfManifestEntry
from src.pdf_extraction import document_id_from_hash, extract_pdf_pages, sha256_file
from src.storage import load_manifest, load_pages, save_manifest, save_pages


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF_DIRECTORY = PROJECT_ROOT / "pdfs"
DEFAULT_DATA_DIRECTORY = PROJECT_ROOT / "data"


PDF_EXTRACTOR = Callable[[Path, str, str], list[ExtractedPdfPage]]


def discover_pdfs(pdf_directory: Path) -> list[Path]:
    """Find PDFs recursively, in deterministic order, within the approved root."""
    if not pdf_directory.is_dir():
        raise ValueError(f"PDF directory does not exist: {pdf_directory}")
    return sorted(
        # sorting for deterministic processing order. This will make sure sorting will always be consistent
        path
        for path in pdf_directory.rglob("*") # recursively traverses subdirectories
        # want to accept pdf, PDF, Pdf any type of pdf extension
        if path.is_file() and path.suffix.lower() == ".pdf"
    )

# Discover all PDF files inside the supplied directory and its subdirectories.
def ingest_pdf_directory(
    pdf_directory: Path,
    data_directory: Path,
    extractor: PDF_EXTRACTOR = extract_pdf_pages,
) -> tuple[int, int]:
    """Ingest new/changed PDFs and remove records for deleted PDFs.

    Returns `(ingested, skipped)`. The content hash, not the filename or
    timestamp, determines whether an existing PDF version may be reused.
    """
    manifest_path = data_directory / "manifest.json"
    pages_path = data_directory / "pages.jsonl"
    
    existing_manifest = load_manifest(manifest_path)
    existing_pages = load_pages(pages_path)
    
    # get all the pdfs available
    discovered_paths = discover_pdfs(pdf_directory)
    
    discovered_relative_paths = {
        path.relative_to(pdf_directory).as_posix() for path in discovered_paths
    }

    new_manifest: dict[str, PdfManifestEntry] = {}
    
    replacement_pages: dict[str, list[ExtractedPdfPage]] = {}
    ingested = 0
    skipped = 0

    for pdf_path in discovered_paths:
        relative_path = pdf_path.relative_to(pdf_directory).as_posix()
        content_hash = sha256_file(pdf_path)
        existing_entry = existing_manifest.get(relative_path)

        if existing_entry and existing_entry.content_hash == content_hash:
            new_manifest[relative_path] = existing_entry
            skipped += 1
            continue

        document_id = document_id_from_hash(content_hash)
        pages = extractor(pdf_path, document_id, relative_path)
        replacement_pages[relative_path] = pages
        
        new_manifest[relative_path] = PdfManifestEntry(
            document_id=document_id,
            relative_path=relative_path,
            content_hash=content_hash,
            modified_at=datetime.fromtimestamp(pdf_path.stat().st_mtime, tz=timezone.utc),
            page_count=len(pages),
            extraction_status="complete" if any(page.text.strip() for page in pages) else "ocr_required",
        )
        ingested += 1

    # Removing stale pages and rebuilding the current state
    retained_pages = [
        page
        for page in existing_pages
        if page.relative_path in discovered_relative_paths
        and page.relative_path not in replacement_pages
    ]
    current_pages = retained_pages + [
        page for pages in replacement_pages.values() for page in pages
    ]

    save_manifest(manifest_path, new_manifest)
    save_pages(pages_path, current_pages)
    return ingested, skipped


def main() -> None:
    ingested, skipped = ingest_pdf_directory(DEFAULT_PDF_DIRECTORY, DEFAULT_DATA_DIRECTORY)
    print(f"PDF ingestion complete: {ingested} ingested, {skipped} unchanged.")
    print(f"Manifest: {DEFAULT_DATA_DIRECTORY / 'manifest.json'}")
    print(f"Extracted pages: {DEFAULT_DATA_DIRECTORY / 'pages.jsonl'}")


if __name__ == "__main__":
    main()
