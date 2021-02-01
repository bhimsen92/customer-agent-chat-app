from flask_socketio import SocketIO

# flask_sqlalchemy takes care creating the declarative base class.
from flask_sqlalchemy import SQLAlchemy


socket_io = SocketIO(manage_session=False)
db = SQLAlchemy()

hash_table = {}


def save_socket(key, sid):
    hash_table[key] = sid


def get_socket(key):
    return hash_table.get(key)


def delete_socket(key):
    hash_table.pop(key, None)
