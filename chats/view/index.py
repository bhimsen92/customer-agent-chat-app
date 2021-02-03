from flask import Blueprint, render_template
from flask import session, redirect, url_for

blueprint = Blueprint("home", __name__)


@blueprint.route("/", methods=["GET"])
def index():
    if "is_customer" in session:
        return redirect(url_for("customer.customer"))
    elif "is_agent" in session and session["is_user_authenticated"]:
        return redirect(url_for("agent.agent_list_conversations"))
    return render_template("index.html")
