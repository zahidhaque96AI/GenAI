
"""JSONL storage operations for the doc-chunking project."""

from pathlib import Path

from src.models import ChunkRecord, ExtractedPdfPage


def load_pages(path: Path) -> list[ExtractedPdfPage]:
    """Load extracted PDF pages from a JSONL file."""

    if not path.exists():
        raise FileNotFoundError(
            f"Input pages file does not exist: {path}"
        )

    pages: list[ExtractedPdfPage] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):

            # Ignore blank lines.
            if not line.strip():
                continue

            try:
                page = ExtractedPdfPage.model_validate_json(line)

            except Exception as exc:
                raise ValueError(
                    f"Invalid page record at line {line_number} "
                    f"in file: {path}"
                ) from exc

            pages.append(page)

    return pages


def save_chunks(
    path: Path,
    chunks: list[ChunkRecord],
) -> None:
    """Save generated chunks to a JSONL file."""

    # Create the output directory if it does not exist.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file before replacing the output.
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:

            for chunk in chunks:
                file.write(chunk.model_dump_json())
                file.write("\n")

        # Replace the destination only after writing completes.
        temporary_path.replace(path)

    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
