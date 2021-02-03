from flask import Blueprint, request
from .customer import CustomerAPI
from .conversation import ConversationAPI
from chats.models import User, Message, agent, conversation_assignment
from sqlalchemy.sql import select, desc, update, insert, and_, asc
from chats.core import db
from chats.utils.session_utils import login_required
from chats.models.agent import AgentStatus
from chats.models.conversation import ConversationStatus


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
        .order_by(asc(message.c.created_at))
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
                "status": result.status.name,
                "created_at": result.created_at,
            }
        )
    return {"items": return_value, "total": len(return_value)}, 200


@blueprint.route("/agents/assign", methods=["POST",])
def assign_agent():
    payload = request.get_json()
    if payload["event_type"] != "assign_agent":
        return {"message": f"Invalid event type: {payload['event_type']}"}, 400
    conversation_id = payload["data"]["conversation_id"]

    # verify that the current conversation has no active assignment.
    query = (
        select([conversation_assignment.c.user_id])
        .select_from(
            conversation_assignment.join(
                agent, conversation_assignment.c.user_id == agent.c.user_id
            )
        )
        .where(
            and_(
                conversation_assignment.c.conversation_id == conversation_id,
                conversation_assignment.c.status.in_(
                    [ConversationStatus.active, ConversationStatus.idle]
                ),
            )
        )
    )
    result = db.session.execute(query)

    if result.rowcount > 1:
        # raise exception. It is a bug in the system.
        pass
    elif result.rowcount == 1:
        user_id = next(result)
        return {"agent_id": user_id, "conversation_id": conversation_id}, 200
    else:
        # find an agent with "available" state.
        # mark it as assigned, also update last_assigned_at [not there at the moment]
        statement = (
            update(agent)
            .where(agent.c.status == AgentStatus.available)
            .values(status=AgentStatus.assigned)
            .returning(agent.c.user_id)
        )
        result = db.session.execute(statement)
        if result.rowcount == 0:
            return {
                "success": False,
                "message": "No agent available at the moment."
            }
        user_id = next(result).user_id

        # add the agent_id to conversation_assignment table.
        # also update table such that the pair (user_id, conversation_id) is unique.
        statement = (
            insert(conversation_assignment)
            .values(user_id=user_id, conversation_id=conversation_id)
            .returning(conversation_assignment.c.id)
        )
        result = db.session.execute(statement)
        assignment_id = next(result).id

        # commit the transaction.
        db.session.commit()
        return {"success": True, "agent_id": user_id, "conversation_assignment_id": assignment_id}, 200
