from datetime import datetime
from backend.database import Base
from sqlalchemy import DateTime, Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from enum import Enum


class ChangeType(Enum):
    Edit = "Edit"
    Delete = "Delete"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_deleted = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    edited_at = Column(DateTime, nullable=True)

    history = relationship("Changes", back_populates="message")
    sender = relationship("Users", foreign_keys=[sender_id])
    group = relationship("Groups", back_populates="messages")
    unread_by = relationship("UnreadMessage", back_populates="message", cascade="all, delete-orphan")


class UnreadMessage(Base):
    __tablename__ = "unread_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)

    user = relationship("Users", foreign_keys=[user_id])
    message = relationship("Messages", back_populates="unread_by")
    group = relationship("Groups")

    __table_args__ = (
        UniqueConstraint('user_id', 'message_id', name='uq_user_message_unread'),
    )


class Changes(Base):
    __tablename__ = "changes"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    change_type = Column(Enum(ChangeType), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = relationship("Messages", back_populates="history")
    editor = relationship("User", foreign_keys=[sender_id])
    original_text = Column(Text, nullable=False)
    new_text = Column(Text, nullable=False)
    created_at =  Column(DateTime, server_default=func.now())