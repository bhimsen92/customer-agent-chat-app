import enum
from chats.core import db
from sqlalchemy import Column, BigInteger, Text, DateTime, Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


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
    _agent = relationship(
        "Agent", back_populates="user_metadata", uselist=False, lazy=True
    )

    def __repr__(self):
        return f"user<{self.id}>: {self.email}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_agent(self):
        return self._agent is not None

    def get_agent(self):
        return self._agent

    @classmethod
    def create(cls, data):
        user = cls(name=data["name"], email=data["email"])
        if "password" in data:
            user.set_password(data["password"])
        if "type" in data:
            user.type = data["type"]
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get(cls, email):
        return cls.query.filter_by(email=email).first()

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "phone_number": self.phone_number,
            "last_active": self.last_active,
            "type": self.type,
            "created_at": self.created_at,
        }
