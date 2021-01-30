import enum
from datetime import datetime
from chats.core import db
from sqlalchemy import BigInteger, Enum, DateTime, Column, ForeignKey
from sqlalchemy.orm import relationship


class Status(enum.Enum):
  available = 1
  not_available = 2
  assigned = 3
  logged_out = 4


class Agent(db.Model):
  id = Column(BigInteger, primary_key=True)
  status = Column(Enum(Status), default=Status.not_available)
  user_id = Column(BigInteger, ForeignKey("user.id"))

  created_at = Column(DateTime, default=datetime.utcnow)

  # relationships
  metadata = relationship("User", back_populates="_agent", lazy="dynamic")