from flask import Blueprint, render_template
from chats.utils.session_utils import get_customer_payload, is_new_customer

blueprint = Blueprint("customer", __name__)


@blueprint.route("/", methods=["GET"])
def customer():
    data = {}
    if not is_new_customer():
        data = get_customer_payload()
    return render_template("customer.html", data=data)
