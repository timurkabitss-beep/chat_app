import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from sqlalchemy import select, update
from backend.routers.auth import router as auth_router
from backend.routers.users import router as users_router
from backend.routers.messages import router as messages_router
from backend.routers.groups import router as groups_router
from backend.routers.websocket import router as ws_router
from backend.database import engine, SessionLocal
from backend.database import Base
from backend.settings.settings import settings
from backend.models.messages import Message
from backend.models.groups import GroupMember
from backend.utils.manager import manager


async def send_scheduled_messages():
    """Background task: check for due scheduled messages and send them."""
    while True:
        try:
            async with SessionLocal() as db:
                now = datetime.now(timezone.utc)
                stmt = (
                    select(Message)
                    .where(
                        Message.scheduled_at.isnot(None),
                        Message.is_sent == False,
                        Message.scheduled_at <= now,
                    )
                )
                res = await db.execute(stmt)
                messages = list(res.scalars().all())

                for msg in messages:
                    msg.is_sent = True

                    if msg.group_id:
                        member_res = await db.execute(
                            select(GroupMember.user_id).where(GroupMember.group_id == msg.group_id)
                        )
                        member_ids = [row[0] for row in member_res.all()]

                        payload = {
                            "type": "group_message",
                            "message_id": msg.id,
                            "group_id": msg.group_id,
                            "sender_id": msg.sender_id,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat() if msg.created_at else None,
                        }
                        await manager.broadcast_to_group(payload, member_ids)

                    elif msg.receiver_id:
                        payload = {
                            "type": "direct_message",
                            "message_id": msg.id,
                            "sender_id": msg.sender_id,
                            "receiver_id": msg.receiver_id,
                            "content": msg.content,
                            "created_at": msg.created_at.isoformat() if msg.created_at else None,
                        }
                        await manager.send_personal_message(payload, msg.sender_id)
                        await manager.send_personal_message(payload, msg.receiver_id)

                await db.commit()

        except Exception as e:
            print(f"[Scheduler] Error: {e}")

        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    task = asyncio.create_task(send_scheduled_messages())
    yield
    task.cancel()
    await engine.dispose()


app = FastAPI(
    title="Chat Application API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(messages_router)
app.include_router(groups_router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat App API!"}
