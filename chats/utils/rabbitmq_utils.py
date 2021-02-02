from collections import defaultdict
from threading import Thread
import pika


class Rabbitmq:
    def __init__(self, app=None):
        self.app = app
        self.callbacks = defaultdict(list)
        self.connection = None
        if self.app:
            self.init_app(app)

    def _setup_message_bus_queue(self, channel):
        # if the queue does not exist
        channel.queue_declare(queue=self.app.config["HOSTNAME"])
        # bind it with message_bus exchange.
        channel.queue_bind(
            exchange=self.app.config["RABBITMQ_PUBSUB_EXCHANGE"],
            queue=self.app.config["HOSTNAME"],
        )

    def init_app(self, app):
        credentials = pika.PlainCredentials(
            app.config["RABBITMQ_USER"], app.config["RABBITMQ_PASSWORD"]
        )
        parameters = pika.ConnectionParameters(
            app.config["RABBITMQ_HOST"], app.config["RABBITMQ_PORT"], "/", credentials
        )
        self.connection = pika.BlockingConnection(parameters)

        # start listening on message bus exchange.
        thread = Thread(
            target=self._listen_for_events_on_message_bus,
            name="listen_message_bus_events",
            daemon=True,
        )
        thread.start()

    def register_callback(self, event_type, callback):
        self.callbacks[event_type].append(callback)

    def publish_message(self, payload):
        # publish message to event bus.
        channel = self.connection.channel()
        # setup queue if not already setup.
        self._setup_message_bus_queue(channel)

        # publish message.
        channel.basic_publish(
            exchange=self.app.config["RABBITMQ_PUBSUB_EXCHANGE"],
            routing_key="",
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
        channel.close()

    def enqueue_background_task(self, payload):
        # publish message to "background_tasks" event queue.
        # event_type should be used as routing key.
        channel = self.connection.channel()

        # publish message
        channel.basic_publish(
            exchange=self.app.config["RABBITMQ_PUBSUB_BACKGROUND_TASKS_EXCHANGE"],
            routing_key=payload["event_type"],
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
        channel.close()

    def _handle_message_bus_events(self, ch, method, properties, body):
        print("message: ", body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _listen_for_events_on_message_bus(self):
        channel = self.connection.channel()

        # setup queue if not already setup.
        self._setup_message_bus_queue(channel)

        channel.basic_consume(
            queue=self.app.config["HOSTNAME"],
            on_message_callback=self._handle_message_bus_events,
        )
        channel.start_consuming()
