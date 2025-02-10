from enum import StrEnum

from pydantic import BaseModel


class UserPermissionsEnum(StrEnum):
    CAN_DELETE_USER: str = "CAN_DELETE_USER"
    CAN_SELF_EDIT: str = "CAN_SELF_EDIT"
    CAN_SELF_DELETE: str = "CAN_SELF_DELETE"


class UserPermissionsModel(BaseModel):
    permissions: UserPermissionsEnum

