import json
import pika
import requests
from argparse import ArgumentParser


def callback_handler(args, ch, method, properties, body):
    response = requests.post(url=f"{args.chat_api_server}/api/agents/assign", json=body)
    response.raise_for_status()
    result = response.json()
    # acknowledge.
    ch.basic_ack(delivery_tag=method.delivery_tag)
    # send notification to the agent.
    print(json.dumps(result, indent=2))


def run(args):
    credentials = pika.PlainCredentials("admin", "admin")
    parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_consume(
        queue="assign_agent", on_message_callback=callback_handler,
    )
    channel.start_consuming()


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
