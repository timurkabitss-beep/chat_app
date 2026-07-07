from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.messages import Message, Changes, ChangeType
from backend.schemas.message import MessageCreate, MessageUpdate
from backend.utils.exceptions import PermissionDeniedError, ResourceNotFoundError

async def create_message(db: AsyncSession, data: MessageCreate, sender_id: int) -> Message:
    new_msg = Message(
        content=data.content,
        sender_id=sender_id,
        group_id=data.group_id
    )

    ## Определяем тип чата и заполняем нужное поле
    if data.group_id:
        new_msg.group_id = data.group_id  ## Групповой чат
    elif data.receiver_id:
        new_msg.receiver_id = data.receiver_id  ## Личный диалог
    else:
        raise ValueError("You need to specify either the group_id or the receiver_id.")

    ##Сохраняем
    await db.flush()
    await db.refresh(new_msg)
    return new_msg


async def get_messages(db: AsyncSession, group_id: int, skip: int = 0, limit: int = 50) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.group_id == group_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def update_message(db: AsyncSession, message_id: int, data: MessageUpdate, user_id: int) -> Message:
    res = await db.execute(select(Message).where(Message.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        raise ResourceNotFoundError(resource_name="Message")

    if msg.sender_id != user_id:
        raise PermissionDeniedError(detail="Only the author can edit the message.")

    change_log = Changes(
        message_id=msg.id,
        change_type=ChangeType.Edit,
        sender_id=user_id,
        original_text=msg.content,
        new_text=new_content
    )
    db.add(change_log)

    msg.content = new_content
    msg.edited_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(msg)
    return msg


async def delete_message(db: AsyncSession, message_id: int, user_id: int) -> bool:
    res = await db.execute(select(Message).where(Message.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        raise ResourceNotFoundError(resource_name="Message")

    change_log = Changes(
        message_id=msg.id,
        change_type=ChangeType.Delete,
        sender_id=user_id,
        original_text=msg.content,
        new_text="[MESSAGE DELETED]"
    )
    db.add(change_log)

    msg.content = "[Message deleted]"
    msg.is_deleted = True
    msg.edited_at = datetime.now(timezone.utc)

    await db.flush()
    return True