from pydantic import AnyUrl, BaseModel


class StripePaymentUrl(BaseModel):
    url: AnyUrl


class SetOrderToClosedSchema(BaseModel):
    is_closed: bool = True
