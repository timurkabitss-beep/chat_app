from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Messages(BaseModel):
    content: str = Field(..., min_length=1, nullable=False)
    group_id: Optional[int] | None
    receiver_id: Optional[int] | None
    received_name: str | None

class MessagesResponse(BaseModel):
    id: int
    content: str
    group_id: Optional[int] | None
    sender_id: int
    created_at: datetime

class Config:
    from_attributes = True