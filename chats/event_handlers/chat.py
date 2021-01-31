from flask import current_app
from flask_socketio import join_room, emit


def handle_join_room(payload):
    current_app.logger.info(f"join_room event: {payload}")
    join_room(payload["room_id"])
    emit("join_room_announcement", payload, to=payload["room_id"])


def handle_send_message(payload):
    current_app.logger.info(f"received message: ${payload}")
    emit("receive_message", payload, to=payload["room_id"])
    return True
