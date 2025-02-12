import aio_pika
import json

from settings import settings


class RabbitMQProducer:
    def __init__(self):
        self.rabbitmq_url = settings.RABBITMQ_URL

    async def send_message(self, message: dict, queue_name: str):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)

            message_json = json.dumps(message)
            await channel.default_exchange.publish(
                aio_pika.Message(body=message_json.encode()),
                routing_key=queue.name,
            )


rabbitmq_producer = RabbitMQProducer()
