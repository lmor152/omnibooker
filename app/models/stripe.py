from typing import Any

from pydantic import BaseModel


class StripeAddress(BaseModel):
    city: str | None
    country: str | None
    line1: str | None
    line2: str | None
    postal_code: str | None
    state: str | None


class PaymentMethodResponse(BaseModel):
    id: str
    object: str
    allow_redisplay: str
    billing_details: dict[str, Any]
    card: dict[str, Any]
    created: int
    customer: str | None
    livemode: bool
    type: str
