from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # Нужен для асинхронных запросов в SQLAlchemy

from utils.security import hash_password, verify_password, create_access_token
from utils.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserInactiveError
)
from schemas.user import UserCreate, UserLogin
from models.user import User

###Асинхронная регистрация нового пользователя.
async def register_user(db: AsyncSession, user_data: UserCreate) -> User:

    # 1. Проверяем username через асинхронный select
    username_query = await db.execute(select(User).filter(User.username == user_data.username))
    existing_username = username_query.scalars().first()
    if existing_username:
        raise UserAlreadyExistsError(field="username")

    # 2. Проверяем email (если он передан)
    if user_data.email:
        email_query = await db.execute(select(User).filter(User.email == user_data.email))
        existing_email = email_query.scalars().first()
        if existing_email:
            raise UserAlreadyExistsError(field="email")

    hashed_password =  hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )

    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return new_user

### Асинхронная авторизация пользователя.
### Проверяет существование пользователя, сверяет пароль и возвращает JWT-токен.
async def login_user(db: AsyncSession, login_data: UserLogin) -> str:

    query = await db.execute(select(User).filter(User.username == login_data.username))
    user = query.scalars().first()

    if not user:
        raise InvalidCredentialsError()

    if hasattr(user, "is_active") and not user.is_active:
        raise UserInactiveError()

    verify_password(login_data.password, user.hashed_password)

    token_data = {"sub": str(user.id)}

    token = create_access_token(data=token_data)
    return token