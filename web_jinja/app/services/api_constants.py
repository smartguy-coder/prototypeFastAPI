from enum import StrEnum


class URLS(StrEnum):
    CATEGORIES = "categories"
    PRODUCTS = "products"
    USERS = "users"
    ORDERS = "orders"
    PAYMENT_HOOKS = "payment-hooks"


class ModeChangeOrderProductQuantityEnum(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"
    SET = "set"
