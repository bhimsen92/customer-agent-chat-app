import enum
from sqlalchemy import BigInteger, ForeignKey, Text, Enum, DateTime, Column
from sqlalchemy.orm import relationship
from datetime import datetime
from chats.core import db


class MessageStatus(enum.Enum):
  received = 1
  delivered = 2
  read = 3


class Message(db.Model):
  id = Column(BigInteger, primary_key=True)
  user_id = Column(BigInteger, ForeignKey("user.id"))
  conversation_id = Column(BigInteger, ForeignKey("conversation.id"))
  text = Column(Text)
  message_status = Column(Enum(MessageStatus), default=MessageStatus.received)
  created_at = Column(DateTime, default=datetime.utcnow)
