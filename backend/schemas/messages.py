from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class Messages(BaseModel):
    content: str = Field(..., min_length=1, max_length=100)
    group_id: Optional[int] | None
    receiver_id: Optional[int] | None
    received_name: str | None

class MessagesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    group_id: Optional[int] = None
    sender_id: int
    created_at: datetime
