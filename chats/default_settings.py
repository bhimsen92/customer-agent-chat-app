import os

HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY", "something-something-secret")
SQLALCHEMY_DATABASE_URI = "postgresql://chats:magical@localhost/chats"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = "filesystem"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "admin"
RABBITMQ_PASSWORD = "admin"

RABBITMQ_PUBSUB_EXCHANGE = "message_bus"
RABBITMQ_PUBSUB_BACKGROUND_TASKS_EXCHANGE = "background_tasks"

HOSTNAME = "webapp-1"
