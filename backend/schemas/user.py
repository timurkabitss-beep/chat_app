from pydantic import BaseModel
from backend.models.user import UserRole

class User(BaseModel):
    id: int
    username: str
    password: str
    email: str | None = None
    role: UserRole
    bio: str | None = None


class CreateUser(BaseModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None

