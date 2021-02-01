from chats.core import create_app
from flask import g, session


def before_request():
    g.is_user_authenticated = session.get("is_user_authenticated", False)


if __name__ == "__main__":
    app, socket_io = create_app()
    app.before_request(before_request)
    socket_io.run(
        app,
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config.get("DEBUG", True),
    )
else:
    app = create_app()
