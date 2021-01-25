from chats.core import create_app

if __name__ == "__main__":
    app, socket_io = create_app()
    socket_io.run(
        app,
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config.get("DEBUG", True),
    )
else:
    app = create_app()
