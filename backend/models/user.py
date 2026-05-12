from datetime import datetime
from backend.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    member = "member"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(Enum(UserRole), default=UserRole.member, nullable=False)
    bio = Column(Text, default="")
    created_at = Column(FateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)

    groups = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    messages_received = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    unread_messages = relationship("UnreadMessage", back_populates="user", foreign_keys="UnreadMessage.user_id")
    # websocket =