
"""Split extracted PDF page text into token-limited RAG chunks."""

import hashlib
import json
import re

from src.config import ChunkingConfig
from src.models import ChunkRecord
from src.tokenizer import Tokenizer


class TextChunker:
    """Create token-limited chunks while preserving page provenance."""

    def __init__(
        self,
        tokenizer: Tokenizer,
        config: ChunkingConfig,
    ) -> None:
        self._tokenizer = tokenizer
        self._config = config

    def chunk_page(
        self,
        document_id: str,
        relative_path: str,
        page_number: int,
        text: str,
    ) -> list[ChunkRecord]:
        """Split one PDF page into overlapping chunks."""

        if not text or not text.strip():
            return []

        units = self._create_units(text)

        chunks: list[ChunkRecord] = []
        current_text = ""

        for unit in units:
            candidate = self._join_text(current_text, unit)

            if self._tokenizer.count_tokens(candidate) <= self._config.chunk_size:
                current_text = candidate
                continue

            # The current chunk is full. Save it before starting another.
            if current_text:
                chunks.append(
                    self._create_chunk(
                        document_id=document_id,
                        relative_path=relative_path,
                        page_number=page_number,
                        chunk_index=len(chunks),
                        text=current_text,
                    )
                )

            # Carry the trailing portion of the previous chunk forward.
            overlap_text = self._get_overlap(current_text)

            # Reduce overlap when necessary to accommodate the next unit.
            while overlap_text:
                candidate = self._join_text(overlap_text, unit)

                if (
                    self._tokenizer.count_tokens(candidate)
                    <= self._config.chunk_size
                ):
                    break

                overlap_words = overlap_text.split()
                overlap_text = " ".join(overlap_words[1:])

            current_text = self._join_text(overlap_text, unit)

        # Save the final chunk.
        if current_text:
            chunks.append(
                self._create_chunk(
                    document_id=document_id,
                    relative_path=relative_path,
                    page_number=page_number,
                    chunk_index=len(chunks),
                    text=current_text,
                )
            )

        return chunks

    def _create_units(self, text: str) -> list[str]:
        """
        Split text into manageable units.

        Splitting order:
        1. Paragraphs
        2. Sentences for oversized paragraphs
        3. Words for oversized sentences
        4. Characters for unusually long words
        """

        units: list[str] = []

        paragraphs = re.split(r"\n\s*\n", text.strip())

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            # Keep a paragraph together when it fits.
            if (
                self._tokenizer.count_tokens(paragraph)
                <= self._config.chunk_size
            ):
                units.append(paragraph)
                continue

            # Split oversized paragraphs into sentences.
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)

            for sentence in sentences:
                sentence = sentence.strip()

                if not sentence:
                    continue

                if (
                    self._tokenizer.count_tokens(sentence)
                    <= self._config.chunk_size
                ):
                    units.append(sentence)
                else:
                    units.extend(self._split_long_sentence(sentence))

        return units

    def _split_long_sentence(self, sentence: str) -> list[str]:
        """Split an oversized sentence at word boundaries."""

        words = sentence.split()
        units: list[str] = []
        current = ""

        for word in words:
            candidate = self._join_text(current, word)

            if (
                self._tokenizer.count_tokens(candidate)
                <= self._config.chunk_size
            ):
                current = candidate
                continue

            if current:
                units.append(current)

            # Handle a word that individually exceeds the token limit.
            if (
                self._tokenizer.count_tokens(word)
                > self._config.chunk_size
            ):
                current = self._split_long_word(word, units)
            else:
                current = word

        if current:
            units.append(current)

        return units

    def _split_long_word(
        self,
        word: str,
        units: list[str],
    ) -> str:
        """
        Split an unusually long word into character-based fragments.

        This is a last-resort fallback for unbroken strings such as
        long identifiers, URLs, or encoded text.
        """

        current = ""

        for character in word:
            candidate = current + character

            if (
                self._tokenizer.count_tokens(candidate)
                <= self._config.chunk_size
            ):
                current = candidate
                continue

            if not current:
                raise ValueError(
                    "A single character exceeds the configured chunk size."
                )

            units.append(current)
            current = character

        return current

    def _get_overlap(self, text: str) -> str:
        """Return trailing complete words within the overlap token budget."""

        if not text or self._config.chunk_overlap == 0:
            return ""

        words = text.split()
        overlap_words: list[str] = []

        for word in reversed(words):
            candidate_words = [word] + overlap_words
            candidate = " ".join(candidate_words)

            if (
                self._tokenizer.count_tokens(candidate)
                > self._config.chunk_overlap
            ):
                break

            overlap_words = candidate_words

        return " ".join(overlap_words)

    @staticmethod
    def _join_text(first: str, second: str) -> str:
        """Join two text segments with a single space."""

        if not first:
            return second

        if not second:
            return first

        return f"{first} {second}"

    def _create_chunk(
        self,
        document_id: str,
        relative_path: str,
        page_number: int,
        chunk_index: int,
        text: str,
    ) -> ChunkRecord:
        """Create a validated chunk record with a deterministic ID."""

        return ChunkRecord(
            chunk_id=self._create_chunk_id(
                document_id=document_id,
                page_number=page_number,
                chunk_index=chunk_index,
                text=text,
            ),
            document_id=document_id,
            relative_path=relative_path,
            page_number=page_number,
            chunk_index=chunk_index,
            text=text,
            token_count=self._tokenizer.count_tokens(text),
            chunker_version=self._config.chunker_version,
        )

    def _create_chunk_id(
        self,
        document_id: str,
        page_number: int,
        chunk_index: int,
        text: str,
    ) -> str:
        """Generate a deterministic ID for the chunk."""

        identity = {
            "document_id": document_id,
            "page_number": page_number,
            "chunk_index": chunk_index,
            "text": text,
            "chunker_version": self._config.chunker_version,
            "chunk_size": self._config.chunk_size,
            "chunk_overlap": self._config.chunk_overlap,
            "tokenizer_encoding": self._config.tokenizer_encoding,
        }

        canonical_identity = json.dumps(
            identity,
            sort_keys=True,
            ensure_ascii=False,
        )

        digest = hashlib.sha256(
            canonical_identity.encode("utf-8")
        ).hexdigest()

        return f"chk-{digest[:24]}"
