import json
import requests
from argparse import ArgumentParser


def callback_handler():
    pass


def run(args):
    payload = {"event_type": "assign_agent", "data": {"conversation_id": 1}}
    response = requests.post(
        url=f"{args.chat_api_server}/api/agents/assign", json=payload
    )
    response.raise_for_status()
    result = response.json()
    print(json.dumps(result, indent=2))


def main():
    arguments = ArgumentParser(description="Agent worker")
    arguments.add_argument(
        "--chat-api-server",
        help="Provide api endpoint for chat server.",
        default="http://localhost:5000",
    )
    arguments.add_argument("--rabbitmq-server", help="RabbitMQ server endpoint.")
    args = arguments.parse_args()
    run(args)


main()
