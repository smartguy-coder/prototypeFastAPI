from enum import StrEnum
from typing import Callable, Union

from handlers import process_new_user_registration, process_new_sms_sending


class SupportedQueues(StrEnum):
    USER_REGISTRATION = "user_registration"
    SMS_SENDING = "sms_sending"

    @classmethod
    def get_queues(cls) -> list[str]:
        return list(cls)

    @classmethod
    def get_handler(cls, queue_name: str) -> Union[Callable, None]:
        handlers = {
            cls.USER_REGISTRATION.value: process_new_user_registration,
            cls.SMS_SENDING.value: process_new_sms_sending,
        }
        return handlers.get(queue_name)
