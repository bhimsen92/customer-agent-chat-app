import enum
from sqlalchemy import BigInteger, ForeignKey, DateTime, Text, Column, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from chats.core import db


class ConversationStatus(enum.Enum):
    active = 1
    not_active = 2
    idle = 3
    closed = 4


class Conversation(db.Model):
    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.active)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, data):
        conversation = cls(name=data["name"])
        db.session.add(conversation)
        db.session.commit()
        return conversation

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "last_active": self.last_active,
            "created_at": self.created_at,
        }


class ConversationAssignment(db.Model):
    __table_name__ = "conversation_assignment"

    id = Column(BigInteger, primary_key=True)
    conversation_id = Column(BigInteger, ForeignKey("conversation.id"))
    user_id = Column(BigInteger, ForeignKey("user.id"))
    status = Column(Enum(ConversationStatus), default=ConversationStatus.active)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create(cls, data):
        assignment = cls(
            conversation_id=data["conversation_id"], user_id=data["user_id"]
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment
