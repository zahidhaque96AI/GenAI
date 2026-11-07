
from datetime import datetime
from pydantic import BaseModel, Field

class PdfManifestEntry(BaseModel):
    document_id: str =Field(min_length=1)
    relative_path : str = Field(min_length=1)
    content_hash: str =Field(min_length=64, max_length=64)
    modified_at : datetime
    page_count : int = Field(ge=0)
    extraction_status: str
    
class ExtractedPdfPage(BaseModel):
    document_id : str = Field(min_length=1)
    relative_path: str = Field(min_length=1)
    page_number : int = Field(ge=0)
    text: str
    