from typing import TYPE_CHECKING

from constants import SupportedQueues
import logging

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)


def setup_queues(channel: "BlockingChannel", queues: list) -> None:
    for queue in queues:
        channel.queue_declare(queue=queue, durable=True)
        log.info("Queue '%s' ensured.", queue)


def consume_messages(channel: "BlockingChannel") -> None:
    queues = SupportedQueues.get_queues()
    setup_queues(channel, queues)

    for queue in queues:
        handler = SupportedQueues.get_handler(queue)
        if handler:
            channel.basic_consume(
                queue=queue,
                on_message_callback=handler,
            )
            log.info("Listening to queue: %s", queue)

    log.info("Waiting for messages...")
    channel.start_consuming()
