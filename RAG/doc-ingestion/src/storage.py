"""Local, readable persistence for the small initial PDF-ingestion project."""

import json
from pathlib import Path

from src.models import ExtractedPdfPage, PdfManifestEntry


def load_manifest(path: Path) -> dict[str, PdfManifestEntry]:
    """Load manifest entries keyed by their PDF path relative to pdfs/."""
    if not path.is_file():
        return {}
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    return {
        relative_path: PdfManifestEntry.model_validate(entry)
        for relative_path, entry in raw_data.items()
    }


def save_manifest(path: Path, manifest: dict[str, PdfManifestEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = {
        relative_path: entry.model_dump(mode="json")
        for relative_path, entry in manifest.items()
    }
    path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")


def load_pages(path: Path) -> list[ExtractedPdfPage]:
    """Load page records from JSON Lines; missing data means an empty index."""
    if not path.is_file():
        return []
    return [
        ExtractedPdfPage.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def save_pages(path: Path, pages: list[ExtractedPdfPage]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(page.model_dump_json() for page in pages)
    path.write_text(f"{content}\n" if content else "", encoding="utf-8")
