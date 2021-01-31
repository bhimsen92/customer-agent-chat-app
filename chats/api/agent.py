from flask.views import MethodView
from flask import request
from chats.models import Agent


class AgentAPI(MethodView):
    def get(self, agent_id):
        if agent_id:
            return self.get_or_404(agent_id)
        else:
            return self.list_agents()

    def post(self):
        data = request.get_json()
        agent = Agent.create(data)
        return {"agent_id": agent.user_id}, 200

    def list_agents(self, agent_id=None):
        results = Agent.list(agent_id=agent_id)
        return_value = []
        for result in results:
            return_value.append(result)
        return return_value, 200

    def get_or_404(self, agent_id):
        results = self.list_agents(agent_id)
        if results:
            user_object = results[0]
            return user_object, 200
        else:
            return {"message": f"Agent with id: {agent_id} does not exist."}, 404
