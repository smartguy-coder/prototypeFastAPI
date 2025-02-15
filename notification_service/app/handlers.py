import json
import logging
from typing import TYPE_CHECKING

from utils.email_sender import send_email, create_body_letter

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
    # try-exept
    body_dict = json.loads(body.decode("utf-8"))
    if not (email := body_dict.get("email")):
        log.error(f"No email provided, {body_dict=}")
        return

    body = create_body_letter(
        lang=body_dict.get("lang", "uk"),
        template_name="user_registration",
        params=body_dict,
    )
    send_email([email], mail_body=body, mail_subject="user_register")
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
