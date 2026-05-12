from datetime import datetime
from backend.database import Base
from sqlalchemy import DateTime, Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum
from backend.models.user import UserRole


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    is_private = Column(Boolean,  default=False)
    description = Column(String(255), nullable=True)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="group")


class GroupMember(Base):
    __tablename__ = 'group_members'

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.member, nullable=False)
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    group = relationship("Groups", back_populates="members")
    user = relationship("Users", back_populates="members")


__table_args__ = (
    UniqueConstraint('group_id', 'user_id', name='uq_user_group'),
)