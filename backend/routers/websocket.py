import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.messages import Message
from backend.models.groups import GroupMember
from backend.services.messages import create_message
from backend.schemas.messages import MessageCreate
from backend.utils.manager import manager
from backend.settings.settings import settings

router = APIRouter(tags=["WebSocket"])


async def authenticate_ws(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    user_id = await authenticate_ws(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(websocket, user_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            msg_type = data.get("type")

            if msg_type == "group_message":
                group_id = data.get("group_id")
                content = data.get("content", "").strip()

                if not group_id or not content:
                    await websocket.send_json({"error": "group_id and content required"})
                    continue

                async with SessionLocal() as db:
                    is_member = await _check_member(db, group_id, user_id)
                    if not is_member:
                        await websocket.send_json({"error": "Not a member of this group"})
                        continue

                    msg_data = MessageCreate(content=content, group_id=group_id)
                    msg = await create_message(db, msg_data, sender_id=user_id)
                    await db.commit()

                    member_ids = await _get_group_member_ids(db, group_id)

                payload = {
                    "type": "group_message",
                    "message_id": msg.id,
                    "group_id": group_id,
                    "sender_id": user_id,
                    "content": content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                await manager.broadcast_to_group(payload, member_ids)

            elif msg_type == "direct_message":
                receiver_id = data.get("receiver_id")
                content = data.get("content", "").strip()

                if not receiver_id or not content:
                    await websocket.send_json({"error": "receiver_id and content required"})
                    continue

                async with SessionLocal() as db:
                    msg_data = MessageCreate(content=content, receiver_id=receiver_id)
                    msg = await create_message(db, msg_data, sender_id=user_id)
                    await db.commit()

                payload = {
                    "type": "direct_message",
                    "message_id": msg.id,
                    "sender_id": user_id,
                    "receiver_id": receiver_id,
                    "content": content,
                    "created_at": msg.created_at.isoformat() if msg.created_at else None,
                }
                await manager.send_personal_message(payload, user_id)
                await manager.send_personal_message(payload, receiver_id)

            elif msg_type == "typing":
                group_id = data.get("group_id")
                receiver_id = data.get("receiver_id")

                payload = {"type": "typing", "user_id": user_id}

                if group_id:
                    async with SessionLocal() as db:
                        member_ids = await _get_group_member_ids(db, group_id)
                    others = [uid for uid in member_ids if uid != user_id]
                    await manager.broadcast_to_group(payload, others)
                elif receiver_id:
                    await manager.send_personal_message(payload, receiver_id)

            elif msg_type == "read":
                group_id = data.get("group_id")
                if group_id:
                    await manager.send_personal_message(
                        {"type": "read_receipt", "user_id": user_id, "group_id": group_id},
                        user_id,
                    )

            else:
                await websocket.send_json({"error": f"Unknown message type: {msg_type}"})

    except WebSocketDisconnect:
        manager.disconnect(user_id)


async def _check_member(db: AsyncSession, group_id: int, user_id: int) -> bool:
    res = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )
    return res.scalar_one_or_none() is not None


async def _get_group_member_ids(db: AsyncSession, group_id: int) -> list[int]:
    res = await db.execute(
        select(GroupMember.user_id).where(GroupMember.group_id == group_id)
    )
    return [row[0] for row in res.all()]
