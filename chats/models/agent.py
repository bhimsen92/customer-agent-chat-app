import enum
from datetime import datetime
from chats.core import db
from sqlalchemy import BigInteger, Enum, DateTime, Column, ForeignKey, exc
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select, update, and_


class AgentStatus(enum.Enum):
    available = 1
    not_available = 2
    assigned = 3
    logged_out = 4


class Agent(db.Model):
    id = Column(BigInteger, primary_key=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.not_available)
    user_id = Column(BigInteger, ForeignKey("user.id"), unique=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    user_metadata = relationship("User", back_populates="_agent", lazy=True)

    @classmethod
    def create(cls, data):
        from chats.models import User
        from chats.models.user import Type

        try:
            data["type"] = Type.not_anonymous
            user = User.create(data)
        except exc.IntegrityError:
            user = User.get(email=data["email"])

        # create agent object.
        try:
            agent = cls(user_id=user.id)
            db.session.add(agent)
            db.session.commit()
        except exc.IntegrityError:
            pass
        return user.get_agent()

    @classmethod
    def list(cls, agent_id=None):
        from chats.models import User

        user, agent = User.__table__, cls.__table__
        query = (
            select([user, agent])
            .select_from(user.join(agent))
            .where(user.c.id == agent.c.user_id)
        )
        if agent_id:
            query.where(user.c.id == agent_id)

        # execute the query.
        results = db.session.execute(query)
        return results

    @classmethod
    def mark_agent_as_not_available_by_use_id(cls, user_id):
        agent = cls.__table__
        statement = (
            update(agent)
            .where(
                and_(
                    agent.c.status != AgentStatus.not_available,
                    agent.c.user_id == user_id,
                )
            )
            .values(status=AgentStatus.not_available)
        )
        db.session.execute(statement)
        db.session.commit()

    @classmethod
    def mark_agent_as_available_by_use_id(cls, user_id):
        agent = cls.__table__
        statement = (
            update(agent)
            .where(
                and_(
                    agent.c.status == AgentStatus.not_available,
                    agent.c.user_id == user_id,
                )
            )
            .values(status=AgentStatus.available)
        )
        db.session.execute(statement)
        db.session.commit()

    @classmethod
    def mark_agents_as_available(cls, conversation_id):
        from chats.models import agent, conversation_assignment
        from chats.models.conversation import ConversationStatus

        # fetch unique user ids.
        user_ids = (
            select([conversation_assignment.c.user_id])
            .select_from(conversation_assignment)
            .where(
                and_(
                    conversation_assignment.c.conversation_id == conversation_id,
                    conversation_assignment.c.status.in_(
                        [ConversationStatus.active, ConversationStatus.idle]
                    ),
                )
            )
            .distinct()
            .alias("user_ids")
        )

        # update agent status, mark it as available only when agent is in assigned state.
        update_query = (
            update(agent)
            .where(
                and_(agent.c.id.in_(user_ids), agent.c.status == AgentStatus.assigned)
            )
            .values(status=AgentStatus.available)
        )

        # use those ids to update agent status.
        db.session.execute(update_query)
        db.session.commit()
