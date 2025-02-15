import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

log = logging.getLogger(__name__)


def process_new_user_registration(
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


def process_new_sms_sending(
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
