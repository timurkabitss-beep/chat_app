from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, UserUpdate
from backend.utils.security import hash_password, verify_password


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    hash_pwd = hash_password(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_pwd,
        full_name=data.full_name or "",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    usr = await db.execute(select(User).where(func.lower(User.username) == username.lower()))
    return usr.scalar_one_or_none()


async def get_users_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate) -> User | None:
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        return None

    upd_data = data.model_dump(exclude_unset=True)

    if "password" in upd_data:
        upd_data["hashed_password"] = hash_password(upd_data.pop("password"))

    for field, value in upd_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> User | None:
    res = await db.execute(select(User).where(User.id == user_id))
    usr = res.scalar_one_or_none()
    if not usr or not usr.is_active:
        return None

    usr.is_active = False
    usr.deleted_at = func.now()
    await db.flush()
    await db.refresh(usr)
    return usr
