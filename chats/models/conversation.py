import enum
from sqlalchemy import BigInteger, ForeignKey, DateTime, Text, Column, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from chats.core import db


class Status(enum.Enum):
  active = 1
  not_active = 2
  idle = 3
  closed = 4


class Conversation(db.Model):
  id = Column(BigInteger, primary_key=True)
  name = Column(Text)
  status = Column(Enum(Status), default=Status.active)

  created_at = Column(DateTime, default=datetime.utcnow)
  last_active = Column(DateTime, default=datetime.utcnow)

  # relationships
  conversation_assignments = relationship("ConversationAssignment", back_populates="conversation", lazy="dynamic")
  messages = relationship("Message", back_populates="conversation", lazy="dynamic")


class ConversationAssignment(db.Model):
  __table_name__ = "conversation_assignment"

  id = Column(BigInteger, primary_key=True)
  conversation_id = Column(BigInteger, ForeignKey("conversation.id"))
  user_id = Column(BigInteger, ForeignKey("user.id"))
  status = Column(Enum(Status), default=Status.active)

  created_at = Column(DateTime, default=datetime.utcnow)

  # relationships
  conversation = relationship("Conversation", back_populates="conversation_assignments", lazy="dynamic")
  user = relationship("User", back_populates="conversation_assignments", lazy="dynamic")