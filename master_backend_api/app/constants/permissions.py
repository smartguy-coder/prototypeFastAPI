from enum import StrEnum

from pydantic import BaseModel


class UserPermissionsEnum(StrEnum):
    CAN_DELETE_USER: str = "CAN_DELETE_USER"
    CAN_SELF_EDIT: str = "CAN_SELF_EDIT"
    CAN_SELF_DELETE: str = "CAN_SELF_DELETE"
    CAN_CREATE_PRODUCT_CATEGORY: str = "CAN_CREATE_PRODUCT_CATEGORY"
    CAN_CREATE_PRODUCT: str = "CAN_CREATE_PRODUCT"


class UserPermissionsModel(BaseModel):
    permissions: UserPermissionsEnum
