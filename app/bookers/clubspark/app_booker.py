import logging
from pathlib import Path
from typing import Annotated, Any

import requests
from pydantic import Field

from app.bookers.clubspark.token_manager import TokenManager
from app.core.config.clubspark import ClubsparkUserConfig
from app.models.clubspark_responses import (
    AppSettingsResponse,
    CreatePaymentResponse,
    GetAvailabilityTimesResponse,
    GetCurrentUserResponse,
    GetUserVenuesResponse,
    GetVenueCreditResponse,
    RequestSessionResponse,
)

Content = Annotated[dict[Any, Any], Field(discriminator="type")]

LOGGER = logging.getLogger(__name__)


class AppBooker:
    def __init__(self, user: ClubsparkUserConfig):
        """
        Initialize the tennis court booker.

        Args:
            user: The ClubsparkUserConfig object containing user information
        """
        self.token_manager = TokenManager(user)

    def _clubspark_headers(self) -> dict[str, str]:
        auth_header = self.token_manager.get_auth_header()
        if not auth_header:
            raise RuntimeError("No valid authentication token available")

        return {
            "accept": "*/*",
            "appname": "cspl",
            "appversion": "2.0",
            "accept-language": "en-NZ,en-AU;q=0.9,en;q=0.8",
            "user-agent": "ClubSparkPlayers/3.7.0 (com.sportlabs.ClubSparkPlayers; build:44; iOS 18.6.2)",
            "authorization": auth_header,
            "accept-encoding": "gzip, deflate, br",
            "cookie": "__cf_bm=XKzsF1h_rlQy9AaDHLA04U9hGHxGw_DJuJqBq7aCxBM-1756918185-1.0.1.1-O69l0L.p2E6oL8c_VvacEQVLvb.xALtXzgob0MAVxFUw9lfW0mqXjMoGk5c5tsYfQ2e43oF9HA7pzFfKxCZ8JbbRmCy0jEBMTnhIcNsl4og",
        }

    def _get_headers(
        self,
        clubspark_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        final_headers: dict[str, str] = {}
        if clubspark_headers:
            final_headers.update(self._clubspark_headers())

        if headers:
            final_headers.update(headers)

        return final_headers

    def _get(
        self,
        url: str,
        clubspark_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        headers = self._get_headers(
            clubspark_headers=clubspark_headers,
            headers=headers,
        )

        LOGGER.debug("GET %s", url)
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code >= 299:
            raise Exception(f"Request failed with status code {response.status_code}")

        return response

    def _post(
        self,
        url: str,
        content: Content,
        clubspark_headers: bool = False,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        headers = self._get_headers(
            clubspark_headers=clubspark_headers,
            headers=headers,
        )

        LOGGER.debug("POST %s %s", url, content)
        response = requests.post(url, json=content, headers=headers, timeout=30)

        if response.status_code >= 299:
            raise Exception(f"Request failed with status code {response.status_code}")

        return response

    def get_current_user(self) -> GetCurrentUserResponse:
        """
        Get the current user's profile information.

        Returns:
            A GetCurrentUserResponse object containing the user's profile information.
        """
        url = "https://api.clubspark.uk/v2/User/GetCurrentUser"
        response = self._get(url, clubspark_headers=True)
        return GetCurrentUserResponse.model_validate(response.json())

    def get_user_venues(self) -> GetUserVenuesResponse:
        url = "https://api.clubspark.uk/v0/Booking/GetUserVenues"
        response = self._get(url, clubspark_headers=True)
        return GetUserVenuesResponse.model_validate(response.json())

    def get_app_settings(self, venue_slug: str):
        url = f"https://api.clubspark.uk/v0/VenueBooking/{venue_slug}/GetAppSettings"
        response = self._get(url, clubspark_headers=True)
        return AppSettingsResponse.model_validate(response.json())

    def get_availability_times(
        self, venue_slug: str, date: str, duration: int = 60, resource_category: int = 1
    ) -> GetAvailabilityTimesResponse:
        url = f"https://api.clubspark.uk/v1/VenueBooking/{venue_slug}/GetAvailabilityTimes?Duration={duration}&Date={date}&resourceCategory={resource_category}"
        response = self._get(url, clubspark_headers=True)
        return GetAvailabilityTimesResponse.model_validate(response.json())

    def get_venue_credit(self, venue_slug: str) -> GetVenueCreditResponse:
        url = f"https://api.clubspark.uk/v0/VenueBooking/{venue_slug}/GetVenueContactCreditsAmount"
        response = self._get(url, clubspark_headers=True)
        return GetVenueCreditResponse.model_validate(response.json())

    def create_payment(
        self,
        user_name: str,
        cost: float,
        scope: str,
        payment_method_id: str,
        venue_id: str,
    ) -> CreatePaymentResponse:
        url = "https://api.clubspark.uk/Payment/CreatePayment"

        content: dict[str, str | float] = {
            "Description": user_name,
            "Cost": cost,
            "PaymentParams": '["booking-default"]',
            "PaymentMethodID": payment_method_id,
            "ScopeID": scope,
            "VenueID": venue_id,
        }
        response = self._post(url, content, clubspark_headers=True)
        return CreatePaymentResponse.model_validate(response.json())

    def request_session(
        self,
        venue_slug: str,
        payment_token: str,
        duration: int,
        date: str,
        total_paid: float,
        start_time: int,
        resource_id: str,
        session_id: str,
    ) -> RequestSessionResponse:
        url = f"https://api.clubspark.uk/v0/VenueBooking/{venue_slug}/RequestSession"

        headers = self._get_headers(clubspark_headers=True)

        content: dict[str, str | int] = {
            "CreditsApplied": "0",
            "PaymentToken": payment_token,
            "Date": date,
            "Duration": duration,
            "Source": "iOS",
            "TotalPaid": str(total_paid),
            "StartTime": start_time,
            "GrossAmount": str(total_paid),
            "ResourceID": resource_id,
            "SessionID": session_id,
            "NetAmount": str(total_paid),
        }

        response = self._post(url, content=content, headers=headers)
        return RequestSessionResponse.model_validate(response.json())
