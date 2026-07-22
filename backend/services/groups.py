from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.groups import Group, GroupMember
from backend.models.user import User, UserRole
from backend.utils.exceptions import UserNotFoundError, PermissionDeniedError, ResourceNotFoundError
from backend.schemas.groups import GroupCreate, GroupUpdate


async def create_group(db: AsyncSession, group_data: GroupCreate, creator_id: int) -> Group:
    new_group = Group(
        name=group_data.name,
        description=group_data.description,
        is_private=group_data.is_private,
    )

    incoming_members = group_data.members or []
    participant_ids = {creator_id} | set(incoming_members)

    group_members_list = []
    for uid in participant_ids:
        res = await db.execute(select(User).where(User.id == uid))
        user = res.scalar_one_or_none()

        if not user or not user.is_active:
            raise UserNotFoundError(identifier=f"user_id={uid}")

        role = UserRole.admin if uid == creator_id else UserRole.member
        group_members_list.append(GroupMember(user_id=user.id, role=role))

    new_group.members = group_members_list

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


async def get_group_by_id(db: AsyncSession, group_id: int) -> Group | None:
    res = await db.execute(select(Group).where(Group.id == group_id))
    return res.scalar_one_or_none()


async def get_group_members(db: AsyncSession, group_id: int) -> list[User]:
    stmt = (
        select(User)
        .join(GroupMember, User.id == GroupMember.user_id)
        .where(GroupMember.group_id == group_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def add_member_to_group(db: AsyncSession, group_id: int, user_id: int, added_by: int) -> GroupMember:
    if not await check_group_admin(db, group_id, added_by):
        raise PermissionDeniedError(detail="Only admins can add members")

    existing = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise PermissionDeniedError(detail="User is already a member")

    user = await db.execute(select(User).where(User.id == user_id))
    if not user.scalar_one_or_none():
        raise UserNotFoundError(identifier=f"user_id={user_id}")

    member = GroupMember(group_id=group_id, user_id=user_id, role=UserRole.member)
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


async def remove_member_from_group(db: AsyncSession, group_id: int, user_id: int, removed_by: int) -> bool:
    if not await check_group_admin(db, group_id, removed_by):
        raise PermissionDeniedError(detail="Only admins can remove members")

    res = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    )
    member = res.scalar_one_or_none()
    if not member:
        raise ResourceNotFoundError(resource_name="GroupMember")

    await db.delete(member)
    await db.flush()
    return True


async def check_group_admin(db: AsyncSession, group_id: int, user_id: int) -> bool:
    stmt = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.role == UserRole.admin,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def check_group_member(db: AsyncSession, group_id: int, user_id: int) -> bool:
    stmt = select(GroupMember).where(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
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
    await db.flush()
    return True
