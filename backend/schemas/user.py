from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from backend.models.user import UserRole

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[str] = None
    role: UserRole
    created_at: datetime
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, description="Min 8 symbols")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)

