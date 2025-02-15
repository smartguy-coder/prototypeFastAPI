from typing import TYPE_CHECKING
from settings import settings
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


def setup_queues(channel: "BlockingChannel", queues: list) -> None:
    for queue in queues:
        channel.queue_declare(queue=queue, durable=True)
        log.info("Queue '%s' ensured.", queue)


def process_new_message(
    ch: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.info("ch: %s", ch)
    log.info("method: %s", method)
    log.info("properties: %s", properties)
    log.info("body: %s", body)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_messages(channel: "BlockingChannel") -> None:
    setup_queues(channel, settings.QUEUES)

    for queue in settings.QUEUES:
        channel.basic_consume(
            queue=queue,
            on_message_callback=process_new_message,
        )
    log.info("Waiting for messages...")
    channel.start_consuming()
