import enum
from sqlalchemy import BigInteger, ForeignKey, Text, Enum, DateTime, Column
from sqlalchemy.orm import relationship
from datetime import datetime
from chats.core import db


class Status(enum.Enum):
  received = 1
  delivered = 2
  read = 3


class Message(db.Model):
  id = Column(BigInteger, primary_key=True)
  user_id = Column(BigInteger, ForeignKey("user.id"))
  conversation_id = Column(BigInteger, ForeignKey("conversation.id"))
  text = Column(Text)
  status = Column(Enum(Status), default=Status.received)
  created_at = Column(DateTime, default=datetime.utcnow)

  # relationships
  user = relationship("User", back_populates="messages", lazy="dynamic")
  conversation = relationship("Conversation", back_populates="messages", lazy="dynamic")