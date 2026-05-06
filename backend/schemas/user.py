from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from backend.models.user import UserRole

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: UserRole
    bio: str | None = None
    created_at: Optional[datetime] = None
    full_mame: Optional[str] = None

class CreateUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, description="Min 8 symbols")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)

