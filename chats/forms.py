from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from chats.models import User


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(message="Not a valid email address")]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Please enter a password")]
    )
    submit = SubmitField("Submit")


class SignupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField(
        "Email", validators=[DataRequired(), Email(message="Not a valid email address")]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Please enter a password")]
    )
    confirmPassword = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password", message="Password must match")],
    )
    submit = SubmitField("Submit")

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")
