"""Note model for DynamoDB."""

from datetime import datetime
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base note model with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, max_length=5000, description="Note content")
    tags: list[str] = Field(default_factory=list, description="Note tags")
    completed: bool = Field(default=False, description="Whether note is completed")


class NoteCreate(NoteBase):
    """Note creation model."""

    pass


class NoteUpdate(BaseModel):
    """Note update model with optional fields."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    tags: Optional[list[str]] = None
    completed: Optional[bool] = None


class Note(NoteBase):
    """Complete note model with DynamoDB fields."""

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique note ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
