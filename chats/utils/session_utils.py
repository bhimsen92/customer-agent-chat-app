from flask import session, g
from functools import wraps
from chats.models import User


def is_new_customer():
    return (
        "user_id" not in session
        or "is_customer" not in session
        or "conversation_id" not in session
    )


def is_new_conversation():
    return "conversation_id" not in session


def get_current_conversation_id():
    return session["conversation_id"]


def get_customer_payload():
    return {
        "conversation_id": session["conversation_id"],
        "user_id": session["user_id"],
    }


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        return_value = (
            {"message": "Please login before performing any operation."},
            401,
        )
        user_id = session.get("user_id")
        if user_id:
            g.user = User.query.filter_by(id=user_id).first()
            if g.user:
                g.is_user_authenticated = True
                return view(*args, **kwargs)
            else:
                return return_value
        else:
            return return_value

    return wrapper


def login(user: User, is_user_authenticated=True) -> None:
    session["user_id"] = user.id
    session["is_user_authenticated"] = is_user_authenticated
    g.user = user
    g.is_user_authenticated = True


def logout(user: User) -> None:
    for k in [
        "user_id",
        "is_user_authenticated",
        "is_agent",
        "is_customer",
        "conversation_id",
    ]:
        session.pop(k, None)
    g.user = None
    g.is_user_authenticated = False


def login_agent(user: User) -> None:
    session["is_agent"] = True
    login(user)


def login_customer(user: User) -> None:
    session["is_customer"] = True
    login(user, is_user_authenticated=False)


def save_conversation_id(conversation_id):
    session["conversation_id"] = conversation_id


def delete_conversation_id():
    session.pop("conversation_id", None)
