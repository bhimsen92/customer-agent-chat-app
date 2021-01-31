from flask import Flask
import chats.default_settings as settings
from chats.extensions import socket_io, db
from chats.event_handlers import chat


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    setup_db(app)
    setup_blueprints(app)
    setup_socket_io(app)
    return app, socket_io


def setup_blueprints(app):
    from chats.view.index import blueprint as index
    from chats.view.customer import blueprint as customer
    from chats.api import blueprint as api
    from chats.view.agent import blueprint as agent

    blueprints = [
        {"handler": index, "url_prefix": "/"},
        {"handler": customer, "url_prefix": "/customer"},
        {"handler": api, "url_prefix": "/api"},
        {"handler": agent, "url_prefix": "/agents"},
    ]

    for bp in blueprints:
        app.register_blueprint(bp["handler"], url_prefix=bp["url_prefix"])


def setup_socket_io(app):
    socket_io.init_app(app)
    socket_io.on_event("join_room", chat.handle_join_room)
    socket_io.on_event("send_message", chat.handle_send_message)
    return socket_io


def setup_db(app):
    db.app = app
    db.init_app(app)
