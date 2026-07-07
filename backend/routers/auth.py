from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from backend.database import SessionDep
from backend.services.auth import register_user, login_user
from backend.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from backend.models.user import User
from backend.utils.security import get_current_user

router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: SessionDep):
    new_user = await register_user(db=db, user_data=user_data)
    return new_user

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(login_data: UserLogin, db: SessionDep):
    token = await login_user(db=db, login_data=login_data)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
