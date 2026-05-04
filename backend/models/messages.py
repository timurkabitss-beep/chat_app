from datetime import datetime
from backend.database import Base
from sqlalchemy import Column, String, Integer, ForeignKeyDateTime
from sqlalchemy.orm import relationship
from enum import Enum


class ChangeType(Enum):
    Edit = "Edit"
    Delete = "Delete"

class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    text = Column(String)
    sender_id = Column(Integer, ForeignKey("users.id"))
    sender_name = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id"))
    history = relationship("Changes", back_populates="message")

class UnreadMessages(Base):
    __tablename__ = "unread_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_name = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)

class Changes(Base):
    __tablename__ = "changes"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    change_type = Column(Enum(ChangeType), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_name = Column(String)
    message = relationship("Message", back_populates="history")
    editor = relationship("User")
    original_text = Column(String, nullable=False)
    new_text = Column(String, nullable=False)
    created_at =  Column(DateTime, default=datetime.now)