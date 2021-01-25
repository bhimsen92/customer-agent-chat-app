from flask import Blueprint, render_template
from chats.forms import JoinRoomForm, ChatForm


blueprint = Blueprint("home", __name__)


@blueprint.route("/", methods=["GET"])
def index():
    form = JoinRoomForm()
    return render_template("index.html", form=form)


@blueprint.route("/chat", methods=["POST"])
def chat():
    form = JoinRoomForm()
    if form.validate_on_submit():
        return render_template(
            "chat.html",
            username=form.username.data,
            room_id=form.room_id.data,
            form=ChatForm(),
        )
    return render_template("index.html", form=form)
