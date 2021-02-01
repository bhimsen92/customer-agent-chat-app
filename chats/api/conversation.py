from flask.views import MethodView
from chats.models import Conversation


class ConversationAPI(MethodView):
    def get(self, conversation_id):
        if conversation_id:
            conversation = Conversation.query.filter_by(id=conversation_id).first()
            return (
                conversation.serialize(),
                200
                if conversation
                else {"message": f"conversation: {conversation_id} does not exist"},
                404,
            )
        else:
            return self.list_conversations(), 200

    def list_conversations(self):
        conversations = Conversation.query.all()
        return_value = []
        for conversation in conversations:
            return_value.append(conversation.serialize())
        return return_value
