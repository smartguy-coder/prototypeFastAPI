from settings import settings

import pika

connection_params = pika.ConnectionParameters(
    host=settings.RABBITMQ_HOSTNAME,
    port=settings.RABBITMQ_AMQP_PORT,
    credentials=pika.PlainCredentials(
        settings.RABBITMQ_DEFAULT_USER,
        settings.RABBITMQ_DEFAULT_PASS,
    ),
)


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        parameters=connection_params,
    )
