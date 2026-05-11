from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] =Field(None, max_length=500)

class GroupMembersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: int
    name: str
    members: List[str]

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_id: int
    username: str
    content: str
    created_at: datetime


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] =Field(None, max_length=500)


