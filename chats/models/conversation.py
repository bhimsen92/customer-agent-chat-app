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

    @classmethod
    def mark_conversation_as_closed(cls, conversation_id):
        conversation = cls.query.filter_by(id=conversation_id).first()
        if conversation:
            conversation.status = ConversationStatus.closed
        db.session.add(conversation)
        db.session.commit()

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

    @classmethod
    def mark_assignments_as_closed(cls, conversation_id):
        cls.query.filter_by(conversation_id=conversation_id).update(
            {ConversationAssignment.status: ConversationStatus.closed}
        )
        db.session.commit()

    @classmethod
    def mark_assignment_as_closed_by_user_id(cls, user_id):
        cls.query.filter_by(user_id=user_id).update(
            {ConversationAssignment.status: ConversationStatus.closed}
        )
        db.session.commit()
