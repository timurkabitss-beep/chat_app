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
    # bio = Column(Text, default="")
    # groups =
    # messages =
    # unread_messages =
    # websocket =