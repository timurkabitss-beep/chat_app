from fastapi import APIRouter, status, Depends, Query
from backend.database import SessionDep
from backend.schemas.groups import GroupCreate, GroupResponse, GroupUpdate, GroupMembersResponse
from backend.services.groups import (
    create_group, get_user_groups, get_group_by_id, get_group_members,
    add_member_to_group, remove_member_from_group, update_group, delete_group,
)
from backend.utils.security import get_current_user
from backend.models.user import User

router = APIRouter(
    prefix="/groups",
    tags=["Groups"],
)


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_new_group(
    data: GroupCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    group = await create_group(db, data, creator_id=current_user.id)
    return group


@router.get("/", response_model=list[GroupResponse])
async def list_my_groups(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    groups = await get_user_groups(db, current_user.id, skip=skip, limit=limit)
    return groups


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: SessionDep):
    group = await get_group_by_id(db, group_id)
    if not group:
        from backend.utils.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError(resource_name="Group")
    return group


@router.get("/{group_id}/members", response_model=GroupMembersResponse)
async def list_group_members(group_id: int, db: SessionDep):
    group = await get_group_by_id(db, group_id)
    if not group:
        from backend.utils.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError(resource_name="Group")

    members = await get_group_members(db, group_id)
    return GroupMembersResponse(
        group_id=group.id,
        name=group.name,
        members=[m.username for m in members],
    )


@router.post("/{group_id}/members/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: int,
    user_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    await add_member_to_group(db, group_id, user_id, added_by=current_user.id)
    return {"detail": "Member added"}


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group_member(
    group_id: int,
    user_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    await remove_member_from_group(db, group_id, user_id, removed_by=current_user.id)


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group_info(
    group_id: int,
    data: GroupUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    group = await update_group(db, group_id, data, user_id=current_user.id)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_group(
    group_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    await delete_group(db, group_id, user_id=current_user.id)
