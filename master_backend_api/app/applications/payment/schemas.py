from pydantic import AnyUrl, BaseModel


class StripePaymentUrl(BaseModel):
    url: AnyUrl
