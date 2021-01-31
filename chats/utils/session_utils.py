from flask import session


def is_new_customer():
  return "_customer_id" not in session


def get_customer_payload():
  return {
    "conversation_id": session["_conversation_id"],
    "customer_id": session["_customer_id"]
  }
