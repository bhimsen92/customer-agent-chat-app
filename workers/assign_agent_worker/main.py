import json
import pika
import requests
from argparse import ArgumentParser
from functools import partial


def callback_handler(args, ch, method, properties, body):
    body = json.loads(body)
    response = requests.post(url=f"{args.chat_api_server}/api/agents/assign", json=body)
    response.raise_for_status()
    result = response.json()
    if result["success"]:
      # acknowledge.
      ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
      ch.basic_nack(method.delivery_tag, False, False)
    # send notification to the agent.
    print(json.dumps(result, indent=2))


def run(args):
    credentials = pika.PlainCredentials("admin", "admin")
    parameters = pika.ConnectionParameters("localhost", 5672, "/", credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="assign_agent", on_message_callback=partial(callback_handler, args),
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
