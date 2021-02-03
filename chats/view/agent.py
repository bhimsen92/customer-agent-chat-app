from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from chats.forms import SignupForm, LoginForm
from chats.models import (
    Agent,
    User,
    ConversationAssignment,
    conversation,
    conversation_assignment,
)
from chats.utils.session_utils import login_agent, logout, login_required
from sqlalchemy.sql import select, and_
from chats.models.conversation import ConversationStatus
from chats.core import db

blueprint = Blueprint("agent", __name__)


@blueprint.route("/login", methods=["GET", "POST"])
def agent_login():
    if g.is_user_authenticated:
        return redirect(url_for("agent.agent_list_conversations"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(email=form.email.data)
        if user and user.is_agent() and user.check_password(form.password.data):
            login_agent(user)
            # mark agent as available.
            Agent.mark_agent_as_available_by_use_id(user.id)
            return redirect(url_for("agent.agent_list_conversations"))
        elif user is None or (user.is_agent() and not user.check_password(form.password.data)):
            flash("Invalid email or password.")
            return redirect(url_for("agent.agent_login"))
        elif not user.is_agent():
            flash(f"{form.email.data} is not registered as agent.")
            return redirect(url_for("agent.agent_login"))
    return render_template(
        "login.html",
        form=form,
        action=url_for("agent.agent_login"),
        sign_up_link=url_for("agent.agent_sign_up"),
    )


@blueprint.route("/logout", methods=["GET",])
@login_required
def agent_logout():
    # do all these in the background. raise "agent_logout" event.
    # also check if conversations are still active. If so raise "assign_agent" event.
    Agent.mark_agent_as_not_available_by_use_id(g.user.id)
    # mark where agent is part of a conversation as closed.
    ConversationAssignment.mark_assignment_as_closed_by_user_id(g.user.id)
    logout(g.user)
    return redirect(url_for("home.index"))


@blueprint.route("/signup", methods=["GET", "POST"])
def agent_sign_up():
    if g.is_user_authenticated:
        return redirect(url_for("agent.agent_list_conversations"))

    form = SignupForm()
    if form.validate_on_submit():
        # create the agent.
        _ = Agent.create(
            {
                "name": form.name.data,
                "email": form.email.data,
                "password": form.password.data,
            }
        )
        return redirect(url_for("agent.agent_login"))
    else:
        return render_template(
            "signup.html", form=form, action=url_for("agent.agent_sign_up")
        )


@blueprint.route("/conversations", methods=["GET",])
@login_required
def agent_list_conversations():
    # get all the conversation ids where current user is assigned which is active, idle
    query = (
        select([conversation.c.id])
        .select_from(
            conversation.join(
                conversation_assignment,
                conversation.c.id == conversation_assignment.c.conversation_id,
            )
        )
        .where(
            and_(
                conversation.c.status == ConversationStatus.active,
                conversation_assignment.c.user_id == g.user.id,
                conversation_assignment.c.status == ConversationStatus.active,
            )
        )
    )
    result = db.session.execute(query)
    return render_template("agent/list_conversations.html", conversations=result)


@blueprint.route("/conversations/<conversation_id>", methods=["GET",])
@login_required
def agent_conversation(conversation_id):
    data = {
        "conversation_id": conversation_id,
        "user_id": g.user.id,
    }
    user = User.query.filter_by(id=data["user_id"]).first()
    data["name"] = user.name
    return render_template("/agent/conversation.html", data=data)
