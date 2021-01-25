from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class JoinRoomForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    room_id = StringField("Room ID", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_room_id(self, field):
        pass


class ChatForm(FlaskForm):
  message = StringField("Message", validators=[DataRequired()])
  send = SubmitField("Send")
