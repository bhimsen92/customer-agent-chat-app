from flask import Blueprint
from .customer import CustomerAPI

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
