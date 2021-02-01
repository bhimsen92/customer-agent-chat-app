from flask import current_app, request, session
from flask_socketio import join_room, emit
from chats.utils.session_utils import (
    save_conversation_id,
    is_new_conversation,
    get_current_conversation_id,
)
from chats.models import Conversation, ConversationAssignment
from chats.extensions import save_socket


def handle_send_message(payload):
    current_app.logger.info(f"send_message: ${payload}")
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

    # return conversation_id
    return {"conversation_id": conversation.id}
