import enum
from backend.database import Base
from sqlalchemy import (
    DateTime,
    Column,
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Text,
    Boolean,
    func,
    Enum as SqlAlchemyEnum
)
from sqlalchemy.orm import relationship


class ChangeType(str, enum.Enum):
    Edit = "Edit"
    Delete = "Delete"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_deleted = Column(Boolean, default=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True, index=True)
    edited_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True, index=True)
    is_sent = Column(Boolean, default=False, index=True)

    history = relationship("Changes", back_populates="message")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
    group = relationship("Group", back_populates="messages")
    unread_by = relationship("UnreadMessage", back_populates="message", cascade="all, delete-orphan")


class UnreadMessage(Base):
    __tablename__ = "unread_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="unread_messages")
    message = relationship("Message", back_populates="unread_by")
    group = relationship("Group")

    __table_args__ = (
        UniqueConstraint('user_id', 'message_id', name='uq_user_message_unread'),
    )


class Changes(Base):
    __tablename__ = "changes"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    change_type = Column(SqlAlchemyEnum(ChangeType), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    new_text = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    message = relationship("Message", back_populates="history")
    editor = relationship("User", foreign_keys=[sender_id])
