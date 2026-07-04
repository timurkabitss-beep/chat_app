from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from .exceptions import TokenExpiredError, InvalidTokenError, InvalidCredentialsError

SECRET_KEY = "SUPER_SECRET_CHAT_KEY_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Указываем эндпоинт, где пользователь будет получать токен (например, /api/auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

##passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> None:
    if not pwd_context.verify(plain_password, hashed_password):
        raise InvalidTokenError("Invalid password")

##jwt

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["H256"])
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError("Token Expired")
    except JWTError:
        raise InvalidTokenError("Invalid token")


##зависимость
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise InvalidTokenError("Invalid token")
    return int(user_id)