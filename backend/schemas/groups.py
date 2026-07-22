from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = False
    members: Optional[List[int]] = None


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_private: bool
    created_at: datetime


class GroupMembersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: int
    name: str
    members: List[str]


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
