import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
import requests
import time

from environs import env

env.read_env()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

CLIENT_ID = env.str("CLIENT_ID")
CLIENT_SECRET = env.str("CLIENT_SECRET")
TOKEN_URL = env.str("TOKEN_URL")


class FT_Client:
    """
    A client for managing OAuth2 access tokens using client credentials flow.

    This class handles token acquisition, automatic refresh, and provides secure access
    to the current access token. It's designed for APIs that use OAuth2 client credentials
    grant type.

    Attributes:
        _client_id (str): The OAuth2 client ID (kept private).
        _client_secret (str): The OAuth2 client secret (kept private).
        _token_url (str): The endpoint URL for token requests.
        _token_data (dict|None): Stores token and metadata. Format:
            {
                "token": str,  # The access token
                "metadata": dict  # Full token response from server
            }
        _expires_in (float|None): Unix timestamp when the current token expires.
    """

    def __init__(self):
        """
        Initializes the client and fetches the first access token.

        Args:
            client_id: OAuth2 client identifier.
            client_secret: OAuth2 client secret.
            token_url: Full URL to the OAuth2 token endpoint.

        Raises:
            requests.HTTPError: If the initial token request fails.
        """
        self._client_id = CLIENT_ID
        self._client_secret = CLIENT_SECRET
        self._token_url = TOKEN_URL
        self._token_data = None
        self._expires_in = None
        self._logger = logging.getLogger("FT_Client")

        self._logger.info("Initializing FT_Client...")
        self._fetch_token()

    @property
    def token(self) -> str:
        """
        The current access token (auto-refreshes if expired).

        Example:
            >>> client = FT_Client(...)
            >>> print(client.token)  # Auto-refreshes if needed
        """
        return self.get_token()

    def get_token(self) -> str:
        """
        Retrieves a valid access token, automatically refreshing if expired.

        Returns:
            str: The current valid access token.

        Note:
            Prints a message to stdout when refreshing expired tokens. In production,
            consider using logging instead.

        Example:
            >>> client = FT_Client("id", "secret", "https://api.example.com/token")
            >>> token = client.get_token()  # Gets token, auto-refreshes if needed
        """
        if not self._token_data or time.time() >= self._expires_in:
            self._logger.warning("Token expired or missing. Refreshing...")
            self._fetch_token()
        return self._token_data["token"]

    def _fetch_token(self) -> None:
        """
        Fetches a new access token from the OAuth2 server and stores it.

        Uses client credentials flow with application/x-www-form-urlencoded content type.
        Updates both the token data and expiration timestamp.

        Raises:
            requests.HTTPError: If the token request fails (4xx/5xx status).
            ValueError: If the token response is malformed.
        """
        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            self._logger.debug(f"Requesting new token from {self._token_url}")
            response = requests.post(self._token_url, data=payload, headers=headers)
            response.raise_for_status()

            token_info = response.json()
            self._token_data = {
                "token": token_info["access_token"],
                "metadata": token_info,
            }

            self._expires_in = time.time() + token_info["expires_in"]
            self._logger.info(
                "Successfully fetched new token. "
                f"Expires in {token_info['expires_in']} seconds."
            )
        except requests.RequestException as e:
            self._logger.error(f"Token fetch failed: {str(e)}", exc_info=True)
            raise
