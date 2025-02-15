from enum import StrEnum


class SupportedQueues(StrEnum):
    USER_REGISTRATION = "user_registration"
    SMS_SENDING = "sms_sending"

    @classmethod
    def get_queues(cls) -> list[str]:
        return list(cls)
