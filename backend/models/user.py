from datetime import datetime
from backend.database import Base
from sqlalchemy import Column
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
    groups = Column("GroupMember", back_populates="user", nullable=False)
    messages = Column(String(1000), ForeignKey("messages.id"), nullable=False)
    unread_messages = Column(String(1000), ForeignKey("unread_messages.id"), nullable=False)
    # websocket =