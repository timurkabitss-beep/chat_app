from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from backend.models.Group import Group

from backend.models.user import UserRole
from backend.utils.exceptions import UserNotFoundError, PermissionDeniedError, ResourceNotFoundError
from backend.schemas.groups import GroupCreate, GroupMembersResponse, GroupUpdate

async def create_group(db: AsyncSession, group: GroupCreate, creator_id: int) -> Group:
    new_group = Group(name=group.name, description=group.description)
    participant_ids = {creator_id} | set(data.members or [])
    group_members_list = []
    for uid in participant_ids:
        res = await db.execute(select(User).where(User.id == uid))
        user = res.scalar_one_or_none()

        if not user or not user.is_active:
            raise UserNotFoundError(identifier=f"user_id={uid}")

        role = UserRole.admin if user_id == creator_id else UserRole.member
        group_members_list.append(GroupMember(group_id=new_group.id, user_id=user.id, role=role))

    db.add(new_group)
    db.add_all(group_members_list)
    await db.commit()
    await db.refresh(new_group)
    return new_group


async def get_user_groups(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50) -> List[Group]:
    stmt = (
        select(Group)
        .join(GroupMember, Group.id == GroupMember.group_id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return result.scalars().all()

async def check_group_admin(db: AsyncSession, group_id: int, user_id: int) -> bool:
    stmt = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == UserRole.admin
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def update_group(db: AsyncSession, group_id: int, data: GroupUpdate, user_id: int) -> Group | None:
    if not await check_group_admin(db, group_id, user_id):
        raise PermissionDeniedError(detail="Once for admins")

    res = await db.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise ResourceNotFoundError(resource_name="Group")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
    return group


async def delete_group(db: AsyncSession, group_id: int, user_id: int) -> bool:
    if not await check_group_admin(db, group_id, user_id):
        raise PermissionDeniedError(detail="Once for admins")

    res = await db.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise ResourceNotFoundError(resource_name="Group")

    await db.delete(group)
    await db.commit()
    return True

