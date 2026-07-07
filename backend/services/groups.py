from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # Для быстрой подгрузки связей

# ИСПРАВЛЕНО: Правильные пути импортов с маленькой буквы
from backend.models.group import Group, GroupMember
from backend.models.user import User, UserRole
from backend.utils.exceptions import UserNotFoundError, PermissionDeniedError, ResourceNotFoundError
from backend.schemas.group import GroupCreate, GroupUpdate


async def create_group(db: AsyncSession, group_data: GroupCreate, creator_id: int) -> Group:
    # 1. Создаем сам объект группы
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        is_private=group_data.is_private
    )

    # 2. Собираем всех участников (создатель + те, кого передали)
    # Если в GroupCreate нет поля members, по умолчанию ставим пустой список
    incoming_members = getattr(group_data, "members", []) or []
    participant_ids = {creator_id} | set(incoming_members)

    group_members_list = []

    # 3. Валидируем каждого участника перед добавлением
    for uid in participant_ids:
        res = await db.execute(select(User).where(User.id == uid))
        user = res.scalar_one_or_none()

        if not user or not user.is_active:

            raise UserNotFoundError(identifier=f"user_id={uid}")
        role = UserRole.admin if uid == creator_id else UserRole.member

        # Создаем запись участника БЕЗ ручного указания group_id
        group_members_list.append(GroupMember(user_id=user.id, role=role))

    # 4. Магия SQLAlchemy: привязываем список участников напрямую к объекту группы
    new_group.members = group_members_list

    # 5. Сохраняем всё одним махом
    db.add(new_group)
    await db.flush()
    await db.refresh(new_group)
    return new_group


async def get_user_groups(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> list[Group]:

    stmt = (
        select(Group)
        .join(GroupMember, Group.id == GroupMember.group_id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def check_group_admin(db: AsyncSession, group_id: int, user_id: int) -> bool:

    stmt = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == UserRole.admin
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def update_group(db: AsyncSession, group_id: int, data: GroupUpdate, user_id: int) -> Group:
    if not await check_group_admin(db, group_id, user_id):
        raise PermissionDeniedError(detail="Only for admins")

    res = await db.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise ResourceNotFoundError(resource_name="Group")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.flush()
    await db.refresh(group)
    return group


async def delete_group(db: AsyncSession, group_id: int, user_id: int) -> bool:
    if not await check_group_admin(db, group_id, user_id):
        raise PermissionDeniedError(detail="Only for admins")

    res = await db.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise ResourceNotFoundError(resource_name="Group")

    await db.delete(group)
    return True
