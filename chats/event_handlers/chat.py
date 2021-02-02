from flask import current_app, request, session
from flask_socketio import join_room, emit
from chats.utils.session_utils import (
    save_conversation_id,
    is_new_conversation,
    get_current_conversation_id,
)
from chats.models import Conversation, ConversationAssignment, Message, User
from chats.models.conversation import ConversationStatus
from chats.extensions import save_socket, get_socket
from chats.core import rabbitmq


def get_active_users_in_conversation(conversation_id):
    active_users = ConversationAssignment.query.filter_by(
        conversation_id=conversation_id, status=ConversationStatus.active
    ).distinct(ConversationAssignment.user_id)
    return [active_user.user_id for active_user in active_users]


def get_receiver_key(user_id, conversation_id):
    active_user_ids = get_active_users_in_conversation(conversation_id)
    receiver_id = set(active_user_ids) - {
        user_id,
    }
    if receiver_id:
        return "%s-%s" % (receiver_id, conversation_id), receiver_id
    return None


def emit_message_to_client(key, receiver_id, message_id, message):
    socket = get_socket(key)
    if socket:
        user = User.query.filter_by(id=receiver_id).first()
        emit(
            "receive_message",
            {
                "event_type": "receive_message",
                "data": {
                    "message": message,
                    "name": user.name,
                    "message_id": message_id,
                },
            },
            room=socket,
        )


def save_message(payload):
    message = Message.create(payload)
    return message


def handle_receive_message(payload):
    receiver_key, receiver_id = get_receiver_key(
        payload["user_id"], payload["conversation_id"]
    )
    if receiver_key:
        emit_message_to_client(receiver_key, receiver_id, payload["message"])


def handle_send_message(payload):
    current_app.logger.info(f"send_message: ${payload}")

    message = save_message(payload)
    payload["message_id"] = message.id

    receiver_key, receiver_id = get_receiver_key(
        payload["user_id"], payload["conversation_id"]
    )
    if receiver_key:
        emit_message_to_client(
            receiver_key, receiver_id, message.id, payload["message"]
        )
    else:
        rabbitmq.publish_message(
            {
                "event_type": "receive_message",
                "data": {
                    "message": payload["message"],
                    "conversation_id": payload["conversation_id"],
                    "user_id": payload["user_id"],
                    "message_id": message.id,
                },
            }
        )
    return True


def start_conversation(payload):
    current_app.logger.info(f"start_conversation: ${payload}")
    if not is_new_conversation():
        return {"conversation_id": get_current_conversation_id()}
    key = "%s-%s" % (payload["user_id"], request.sid,)

    # create conversation object.
    conversation = Conversation.create({"name": key})

    # create conversation assignment.
    _ = ConversationAssignment.create(
        {"conversation_id": conversation.id, "user_id": payload["user_id"]}
    )

    # save "customer_user_id_conversation_id" key in the hash_table.
    key = "%s-%s" % (payload["user_id"], conversation.id,)
    save_conversation_id(conversation.id)
    save_socket(key, request.sid)

    # emit "assign_agent" event to rabbitmq
    rabbitmq.enqueue_background_task(
        {"event_type": "assign_agent", "data": {"conversation_id": conversation.id}}
    )

    # return conversation_id
    return {"conversation_id": conversation.id}
