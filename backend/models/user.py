from backend.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SqlAlchemyEnum, func, Boolean
from sqlalchemy.orm import relationship
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True, unique=True)
    role = Column(SqlAlchemyEnum(UserRole), default=UserRole.member, nullable=False)
    full_name = Column(String(100), nullable=False, default="")
    bio = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)

    groups = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    messages_received = relationship("Message", back_populates="receiver", foreign_keys="Message.receiver_id")
    unread_messages = relationship("UnreadMessage", back_populates="user", foreign_keys="UnreadMessage.user_id")
