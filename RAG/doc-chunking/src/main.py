
import argparse
from pathlib import Path

from src.chunker import TextChunker
from src.config import ChunkingConfig
from src.storage import load_pages, save_chunks
from src.tokenizer import TiktokenTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert extracted PDF pages into RAG chunks."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "input" / "pages.jsonl",
        help="Path to the extracted pages JSONL file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "output" / "chunks.jsonl",
        help="Path for the generated chunks JSONL file.",
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Maximum number of tokens per chunk.",
    )

    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=75,
        help="Target overlap between adjacent chunks.",
    )

    parser.add_argument(
        "--tokenizer-encoding",
        type=str,
        default="cl100k_base",
        help="Tiktoken encoding name.",
    )

    return parser.parse_args()


def run(
    input_path: Path,
    output_path: Path,
    config: ChunkingConfig,
) -> tuple[int, int]:
    """Run the complete page-to-chunk processing pipeline."""

    pages = load_pages(input_path)

    tokenizer = TiktokenTokenizer(
        encoding_name=config.tokenizer_encoding
    )

    chunker = TextChunker(
        tokenizer=tokenizer,
        config=config,
    )

    all_chunks = []

    for page in pages:
        page_chunks = chunker.chunk_page(
            document_id=page.document_id,
            relative_path=page.relative_path,
            page_number=page.page_number,
            text=page.text,
        )

        all_chunks.extend(page_chunks)

    save_chunks(output_path, all_chunks)

    return len(pages), len(all_chunks)


def main() -> None:
    args = parse_arguments()

    config = ChunkingConfig(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        tokenizer_encoding=args.tokenizer_encoding,
    )

    page_count, chunk_count = run(
        input_path=args.input,
        output_path=args.output,
        config=config,
    )

    print("Chunking completed successfully.")
    print(f"Pages processed : {page_count}")
    print(f"Chunks created  : {chunk_count}")
    print(f"Output file     : {args.output}")


if __name__ == "__main__":
    main()
