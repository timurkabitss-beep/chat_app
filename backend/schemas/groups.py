from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CreateGroup(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] =Field(None, max_length=500)

class GetMembersResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: int
    name: str
    members: list[str]

class GetMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    content: str
    created_at: datetime




class UpdateGroupRequest(BaseModel):
    name: Optional[str] = Field(..., min_length=1, max_length=100)
    description: Optional[str] =Field(None, max_length=500)


