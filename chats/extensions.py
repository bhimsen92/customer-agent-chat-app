from flask_socketio import SocketIO

# flask_sqlalchemy takes care creating the declarative base class.
from flask_sqlalchemy import SQLAlchemy


socket_io = SocketIO()
db = SQLAlchemy()
