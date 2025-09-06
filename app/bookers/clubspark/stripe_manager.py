import logging
from typing import Annotated, Any

import requests
from pydantic import Field

from app.models.stripe import PaymentMethodResponse

Content = Annotated[dict[Any, Any], Field(discriminator="type")]

LOGGER = logging.getLogger(__name__)


class StripeManager:
    def __init__(self):
        """
        Initialize the tennis court booker.
        """

    def _stripe_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _get_headers(
        self,
        stripe_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        final_headers: dict[str, str] = {}
        if stripe_headers:
            final_headers.update(self._stripe_headers())

        if headers:
            final_headers.update(headers)

        return final_headers

    def _get(
        self,
        url: str,
        stripe_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        request_headers = self._get_headers(
            stripe_headers=stripe_headers,
            headers=headers,
        )

        LOGGER.debug("GET %s", url)
        response = requests.get(url, headers=request_headers, timeout=30)

        if response.status_code >= 299:
            raise Exception(f"Request failed with status code {response.status_code}")

        return response

    def _post(
        self,
        url: str,
        content: Content,
        stripe_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        headers = self._get_headers(
            stripe_headers=stripe_headers,
            headers=headers,
        )

        LOGGER.debug("POST %s %s", url, content)
        response = requests.post(url, data=content, headers=headers, timeout=30)

        if response.status_code >= 299:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )

        return response

    def payment_method(
        self,
        stripe_key: str,
        stripe_account: str,
        email: str,
        card_number: str,
        card_exp_month: str,
        card_exp_year: str,
        card_cvc: str,
    ) -> PaymentMethodResponse:
        """
        Get the current user's profile information.

        Returns:
            A GetCurrentUserResponse object containing the user's profile information.
        """
        url = "https://api.stripe.com/v1/payment_methods"

        headers = {
            "Authorization": f"Bearer {stripe_key}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Stripe-Account": stripe_account,
        }

        content = {
            "allow_redisplay": "unspecified",
            "billing_details[email]": email,
            "card[cvc]": card_cvc,
            "card[exp_month]": card_exp_month,
            "card[exp_year]": card_exp_year,
            "card[number]": card_number,
            "payment_user_agent": "stripe-ios/24.0.0; variant.payments-ui; STPPaymentCardTextField",
            "type": "card",
        }

        response = self._post(
            url, content=content, headers=headers, stripe_headers=False
        )
        return PaymentMethodResponse.model_validate(response.json())
