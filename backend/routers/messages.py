from fastapi import APIRouter, status, Depends, Query
from backend.database import SessionDep
from backend.schemas.messages import MessageCreate, MessageUpdate, MessageResponse
from backend.services.messages import create_message, get_group_messages, get_direct_messages, update_message, delete_message
from backend.services.groups import check_group_member
from backend.utils.security import get_current_user
from backend.models.user import User
from backend.utils.exceptions import PermissionDeniedError
from sqlalchemy import and_

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    if data.group_id:
        is_member = await check_group_member(db, data.group_id, current_user.id)
        if not is_member:
            raise PermissionDeniedError(detail="You are not a member of this group")

    msg = await create_message(db, data, sender_id=current_user.id)
    return msg


@router.post("/schedule", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def schedule_message(
    data: MessageCreate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    if not data.scheduled_at:
        raise PermissionDeniedError(detail="scheduled_at is required")

    from datetime import datetime, timezone
    if data.scheduled_at <= datetime.now(timezone.utc):
        raise PermissionDeniedError(detail="scheduled_at must be in the future")

    if data.group_id:
        is_member = await check_group_member(db, data.group_id, current_user.id)
        if not is_member:
            raise PermissionDeniedError(detail="You are not a member of this group")

    data_copy = data.model_copy()
    data_copy.scheduled_at = data.scheduled_at
    msg = await create_message(db, data_copy, sender_id=current_user.id, is_scheduled=True)
    return msg


@router.get("/group/{group_id}", response_model=list[MessageResponse])
async def list_group_messages(
    group_id: int,
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    is_member = await check_group_member(db, group_id, current_user.id)
    if not is_member:
        raise PermissionDeniedError(detail="You are not a member of this group")

    messages = await get_group_messages(db, group_id, skip=skip, limit=limit)
    return messages


@router.get("/direct/{other_user_id}", response_model=list[MessageResponse])
async def list_direct_messages(
    other_user_id: int,
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    messages = await get_direct_messages(db, current_user.id, other_user_id, skip=skip, limit=limit)
    return messages


@router.patch("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: int,
    data: MessageUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    msg = await update_message(db, message_id, data, user_id=current_user.id)
    return msg


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_message(
    message_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    await delete_message(db, message_id, user_id=current_user.id)


@router.delete("/scheduled/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_message(
    message_id: int,
    db: SessionDep,
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from backend.models.messages import Message

    res = await db.execute(select(Message).where(Message.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        from backend.utils.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError(resource_name="Message")
    if msg.sender_id != current_user.id:
        raise PermissionDeniedError(detail="Only the author can cancel this message")
    if msg.is_sent:
        raise PermissionDeniedError(detail="Message already sent")

    await db.delete(msg)
    await db.commit()
