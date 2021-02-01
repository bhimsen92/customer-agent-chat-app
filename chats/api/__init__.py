from flask import Blueprint
from .customer import CustomerAPI
from .conversation import ConversationAPI
from chats.models import User, Message
from sqlalchemy.sql import select, desc
from chats.core import db
from chats.utils.session_utils import login_required


blueprint = Blueprint("api", __name__)


@blueprint.route("/", methods=["GET"])
def index():
    return "welcome to customer-agent api urls."


def register_api(view, endpoint, url, pk="id", pk_type="int"):
    view_func = view.as_view(endpoint)
    blueprint.add_url_rule(
        url, defaults={pk: None}, view_func=view_func, methods=["GET",]
    )
    blueprint.add_url_rule(url, view_func=view_func, methods=["POST",])
    blueprint.add_url_rule(
        "%s<%s:%s>" % (url, pk_type, pk),
        view_func=view_func,
        methods=["GET", "PUT", "DELETE"],
    )


register_api(CustomerAPI, "api_customers", "/customers", pk="customer_id")
register_api(ConversationAPI, "api_conversations", "/conversations", pk="customer_id")


@blueprint.route("/conversations/<conversation_id>/messages", methods=["GET",])
@login_required
def get_conversation_messages(conversation_id):
    user, message = User.__table__, Message.__table__
    query = (
        select(
            [
                message.c.id,
                message.c.conversation_id,
                message.c.text,
                message.c.status,
                message.c.created_at,
                user.c.name,
                user.c.email,
            ]
        )
        .select_from(message.join(user))
        .where(message.c.user_id == user.c.id)
        .where(message.c.conversation_id == conversation_id)
        .order_by(desc(message.c.created_at))
    )
    results = db.session.execute(query)
    return_value = []
    for result in results:
        return_value.append(
            {
                "id": result.id,
                "name": result.name,
                "email": result.email,
                "conversation_id": result.conversation_id,
                "text": result.text,
                "status": result.status,
                "created_at": result.created_at,
            }
        )
    return {"items": return_value, "total": len(return_value)}, 200
