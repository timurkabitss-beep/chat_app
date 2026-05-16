from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from backend.models.User import User

from backend import models
from backend.schemas.user import UserCreate, UserResponse


async def create_user(db: AsyncSession, data: UserCreate)-> models.User:
    hash_pwd = get_password_hash(data.password)
    user = User(username=data.username,
                email=data.email,
                hashed_password=hash_pwd,
                )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate)->models.User | None:
    res = await db.execute(select(User).where(User.user_id==user_id))
    user = res.scalar_one_or_none()

    if not user:
        return None

    upd_data = data.model_dump(exclude_unset=True)

    if "password" in upd_data:
        upd_data["hashed_password"] = get_password_hash(upd_data.pop("password"))

    for field, value in upd_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_username(db: AsyncSession, username: str) -> models.User | None:
    usr = await db.execute(select(User).where(func.lower(User.username) ==username.lower()))
    user = usr.scalar_one_or_none()
    if not user:
        return None
    return user


async def get_users_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.User] | None:
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )

    users = result.scalars().all()
    return users