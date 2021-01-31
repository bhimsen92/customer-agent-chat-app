from flask import Blueprint, request, render_template, redirect, url_for, g, flash
from chats.forms import SignupForm, LoginForm
from chats.models import Agent, User
from chats.utils.session_utils import login_agent, logout, login_required

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
            return redirect(url_for("agent.agent_list_conversations"))
        elif user is None or not user.check_password(form.password.data):
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
    return render_template("agent/list_conversations.html")


@blueprint.route("/conversations/<conversation_id>", methods=["GET",])
@login_required
def agent_conversation():
    return render_template("/agent/conversation.html")
