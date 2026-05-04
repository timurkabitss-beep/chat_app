from datetime import datetime
from backend.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    member = "member"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(Enum(UserRole), default=UserRole.member, nullable=False)
    bio = Column(Text, default="")
    groups = relationship("GroupMember", back_populates="user", nullable=False)
    messages = relationship(String(1000), ForeignKey("messages.id"), nullable=False)
    unread_messages = relationship(String(1000), ForeignKey("unread_messages.id"), nullable=False)
    # websocket =