from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000)
    group_id: Optional[int] | None = None
    receiver_id: Optional[int] | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    group_id: Optional[int] = None
    sender_id: int
    sender_username: Optional[str] = None
    created_at: datetime
