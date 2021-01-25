import os

HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY", "something-something-secret")
