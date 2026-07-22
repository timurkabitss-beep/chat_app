from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000)
    group_id: Optional[int] = None
    receiver_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class MessageUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=3000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    group_id: Optional[int] = None
    sender_id: int
    sender_username: Optional[str] = None
    created_at: datetime
    edited_at: Optional[datetime] = None
    is_deleted: bool = False
    scheduled_at: Optional[datetime] = None
    is_sent: bool = False
