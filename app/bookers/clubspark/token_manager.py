import base64
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from jose import jwt

from app.core.config.clubspark import ClubsparkUserConfig

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages OAuth2 tokens for ClubSpark API with automatic refresh"""

    def __init__(self, user_config: ClubsparkUserConfig):
        self.user_config = user_config
        self.config_file = Path(f"{user_config.id}_clubspark_tokens.json")

        # OAuth2 client credentials (from your captured traffic)
        self.client_id = "clubspark-app"
        self.client_secret = "VA7VqUK4DTECuy9vcDEdzFZZx/rl6iD8eEfL+yfbr1U="
        self.token_url = "https://account.lta.org.uk/issue/oauth2/token"

        # Create basic auth header once
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.basic_auth_header = f"Basic {encoded_credentials}"

        # Initialize tokens dict before loading
        self.tokens: dict[str, Any] = {}
        self.tokens = self._load_tokens()

    def _load_tokens(self) -> dict[str, Any]:
        """Load tokens from JSON file"""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to load tokens: {e}")
                return {}
        else:
            # No tokens file exists, try to fetch initial token
            logger.info("No tokens file found, attempting to fetch initial token")
            if self._fetch_initial_token():
                return self.tokens
            else:
                logger.error("Failed to fetch initial token")
                return {}

    def _save_tokens(self) -> None:
        """Save tokens to JSON file"""
        try:
            self.config_file.write_text(json.dumps(self.tokens, indent=2))
            logger.debug("Tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")

    def set_refresh_token(self, refresh_token: str) -> None:
        """Set the refresh token (typically done once during setup)"""
        self.tokens["refresh_token"] = refresh_token
        self.tokens["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_tokens()
        logger.info("Refresh token updated")

    def get_refresh_token(self) -> Optional[str]:
        """Get the current refresh token"""
        return self.tokens.get("refresh_token")

    def get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary"""
        # Check if we have a valid access token
        if self._is_access_token_valid():
            return self.tokens.get("access_token")

        # Try to refresh the token
        if self._refresh_access_token():
            return self.tokens.get("access_token")

        # No valid token available
        return None

    def _is_access_token_valid(self) -> bool:
        """Check if the current access token is still valid"""
        access_token = self.tokens.get("access_token")
        if not access_token:
            return False

        try:
            # Decode JWT without verification to check expiry
            payload = jwt.get_unverified_claims(access_token)
            exp = payload.get("exp", 0)

            # Add 5-minute buffer before expiry
            buffer_seconds = 300
            current_time = datetime.now(timezone.utc).timestamp()

            is_valid = current_time < (exp - buffer_seconds)
            logger.debug(
                f"Token valid: {is_valid}, expires at: {datetime.fromtimestamp(exp)}"
            )
            return is_valid

        except Exception as e:
            logger.warning(f"Failed to decode token: {e}")
            return False

    def _fetch_initial_token(self) -> bool:
        """Fetch the initial token using username/password grant"""
        if not self.user_config.username or not self.user_config.password:
            logger.error("Username or password not configured")
            return False

        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "authorization": self.basic_auth_header,
            "user-agent": "ClubSpark%20Booker/44 CFNetwork/3826.600.41 Darwin/24.6.0",
            "accept-language": "en-NZ,en-AU;q=0.9,en;q=0.8",
        }

        data = {
            "password": self.user_config.password,
            "scope": "https://api.clubspark.uk/token/",
            "grant_type": "password",
            "username": self.user_config.username,
        }

        try:
            logger.info("Fetching initial token using username/password...")
            response = requests.post(self.token_url, headers=headers, json=data)
            response.raise_for_status()

            token_data = response.json()

            # Update stored tokens
            self.tokens.update(
                {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data["refresh_token"],
                    "expires_in": token_data["expires_in"],
                    "token_type": token_data["token_type"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            self._save_tokens()
            logger.info("Initial token fetched successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to fetch initial token: {e}")
            if hasattr(e, "response") and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error fetching initial token: {e}")
            return False

    def _refresh_access_token(self) -> bool:
        """Refresh the access token using the refresh token"""
        refresh_token = self.get_refresh_token()
        if not refresh_token:
            logger.error("No refresh token available")
            return False

        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "authorization": self.basic_auth_header,
            "user-agent": "ClubSpark%20Booker/44 CFNetwork/3826.600.41 Darwin/24.6.0",
            "accept-language": "en-NZ,en-AU;q=0.8",
        }

        data = {
            "grant_type": "refresh_token",
            "scope": "https://api.clubspark.uk/token/",
            "refresh_token": refresh_token,
        }

        try:
            logger.info("Refreshing access token...")
            response = requests.post(self.token_url, headers=headers, json=data)
            response.raise_for_status()

            token_data = response.json()

            # Update stored tokens
            self.tokens.update(
                {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data["refresh_token"],
                    "expires_in": token_data["expires_in"],
                    "token_type": token_data["token_type"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            self._save_tokens()
            logger.info("Access token refreshed successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            if hasattr(e, "response") and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error refreshing token: {e}")
            return False

    def get_auth_header(self) -> Optional[str]:
        """Get the authorization header value for ClubSpark API calls"""
        access_token = self.get_access_token()
        if access_token:
            return f"Lta-Auth {access_token}"
        return None

    def force_refresh(self) -> bool:
        """Force refresh the access token even if current one is valid"""
        return self._refresh_access_token()

    def clear_tokens(self) -> None:
        """Clear all stored tokens"""
        self.tokens.clear()
        if self.config_file.exists():
            self.config_file.unlink()
        logger.info("All tokens cleared")

    def get_token_info(self) -> dict[str, Any]:
        """Get information about current tokens (for debugging)"""
        access_token = self.tokens.get("access_token")
        info: dict[str, Any] = {
            "has_refresh_token": bool(self.get_refresh_token()),
            "has_access_token": bool(access_token),
            "access_token_valid": self._is_access_token_valid(),
            "updated_at": self.tokens.get("updated_at"),
        }

        if access_token:
            try:
                payload = jwt.get_unverified_claims(access_token)
                info.update(
                    {
                        "expires_at": datetime.fromtimestamp(
                            payload.get("exp", 0)
                        ).isoformat(),
                        "username": payload.get("unique_name"),
                        "email": payload.get(
                            "http://identityserver.thinktecture.com/claims/profileclaims/emailaddress"
                        ),
                    }
                )
            except Exception as e:
                info["token_decode_error"] = str(e)

        return info
