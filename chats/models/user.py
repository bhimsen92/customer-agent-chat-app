import enum
from chats.core import db
from sqlalchemy import Column, BigInteger, Text, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship


class Type(enum.Enum):
  anonymous = 1
  not_anonymous = 2


class User(db.Model):
  id = Column(BigInteger, primary_key=True)

  name = Column(Text, index=True)
  email = Column(Text, index=True, unique=True)
  phone_number = Column(Text, index=True, unique=True)
  password_hash = Column(Text)
  type = Column(Enum(Type), default=Type.anonymous)

  last_active = Column(DateTime)
  created_at = Column(DateTime, default=datetime.utcnow)


  # relationships.
  _agent = relationship("Agent", back_populates="metadata", lazy="dynamic")
  conversation_assignments = relationship("ConversationAssignment", back_populates="user", lazy="dynamic")
  messages = relationship("Message", back_populates="user", lazy="dynamic")

  def __repr__(self):
    return f"user<{self.id}>: {self.email}"

  def is_agent(self):
    return self._is_agent is not None