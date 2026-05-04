from datetime import datetime
from backend.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum
from backend.models.user import UserRole


class Groups(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    members = relationship("GroupMembers", back_populates="group")
    messages = relationship("Messages", back_populates="group")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GroupMembers(Base):
    __tablename__ = 'group_members'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.member, nullable=False)
    group = relatioтship("Groups", back_populates="members")
    user = relationship("Users", back_populates="members")