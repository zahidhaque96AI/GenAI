from enum import Enum
from pydantic import BaseModel, Field

class TicketCategory(str, Enum):
    BILLING = "billing"
    LOGIN = "login"
    TECHNICAL = "technical"
    OTHER = "other"
    
class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketTriage(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    summary: str = Field(
        min_length=1,
        max_length=240,
        description="Concise summary of the reported issue."
    )
    requires_human_review: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(
        min_length=1,
        max_length=300,
        description="Short explanation based only on the ticket content."
    )
