
from pydantic import BaseModel, Field


class ExtractedPdfPage(BaseModel):
    """Represents an extracted PDF page received from doc-ingestion."""

    document_id: str = Field(min_length=1)
    relative_path: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    text: str


class ChunkRecord(BaseModel):
    """Represents a chunk created from an extracted PDF page."""

    chunk_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    relative_path: str = Field(min_length=1)
    page_number: int = Field(ge=1)
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    token_count: int = Field(ge=1)
    chunker_version: str = Field(min_length=1)
