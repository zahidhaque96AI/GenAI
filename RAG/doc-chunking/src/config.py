
from pydantic import BaseModel, Field, model_validator

class ChunkingConfig(BaseModel):
    # configuration controlling the chunking behaviour
    
    chunk_size: int = Field(dafault=500, ge=0)
    chunk_overlap: int = Field(dafault=75, ge=0)
    tokenizer_encoding: str = "cl100k_base"
    chunker_version: str = "1.0"
    
    @model_validator(mode="after")
    def validate_overlap(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk overlap should be less than chunk size")
        return self