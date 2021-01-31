import enum
from datetime import datetime
from chats.core import db
from sqlalchemy import BigInteger, Enum, DateTime, Column, ForeignKey, exc
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select


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

        try:
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
