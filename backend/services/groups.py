from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from backend.models.Group import Group

from backend.models.user import UserRole
from backend.utils.exceptions import UserNotFoundError
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


async def get_user_groups(db: AsyncSession, creator_id: int) -> List[Group]: