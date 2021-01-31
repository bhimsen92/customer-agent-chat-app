from flask import request
from flask.views import MethodView
from chats.models import User, Agent
from chats.core import db
from sqlalchemy import exc


class CustomerAPI(MethodView):
    def get(self, customer_id):
        if customer_id:
            user = User.query.filter_by(id=customer_id).first()
            if not user or user.is_agent():
                return (
                    {
                        "message": f"Customer with {customer_id} does not exist in database."
                    },
                    404,
                )
            return user.serialize(), 200
        else:
            return self.list_customers()

    def post(self):
        # get request payload.
        payload = request.get_json()
        # construct user object. [#TODO needs validation]
        user = User(email=payload["email"], name=payload["name"])
        try:
            # store the object.
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            # catch any integrity execeptions and return appropriate messages(return the user_id).
            db.session.rollback()
            user = User.query.filter_by(email=payload["email"]).first()
        return {"customer_id": user.id}, 200

    def list_customers(self):
        sq = Agent.query(Agent.id).subquery("sq")
        users = User.query.filter_by(~User.id.in_(sq)).all()
        result = [user.serialize() for user in users]
        return result, 200
