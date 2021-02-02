from flask import Blueprint, render_template, session, g, redirect, url_for
from chats.utils.session_utils import (
    get_customer_payload,
    is_new_customer,
    login_required,
    logout,
)
from chats.models import User, Conversation, ConversationAssignment, Agent

blueprint = Blueprint("customer", __name__)


@blueprint.route("/", methods=["GET"])
def customer():
    data = {}
    if not is_new_customer():
        data = get_customer_payload()
    return render_template(
        "customer.html",
        data=data,
        customer_logout_link=url_for("customer.customer_logout"),
    )


@blueprint.route("/logout", methods=["GET",])
@login_required
def customer_logout():
    Conversation.mark_conversation_as_closed(session["conversation_id"])
    Agent.mark_agents_as_available(session["conversation_id"])
    ConversationAssignment.mark_assignments_as_closed(session["conversation_id"])

    # send event that conversation is closed.
    # rabbitmq.emit("conversation_closed", {"conversation_id": session["conversation_id"]})

    logout(g.user)
    return redirect(url_for("home.index"))
