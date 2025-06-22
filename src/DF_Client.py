import requests
import time

class DF_Client:
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
        _expires_at (float|None): Unix timestamp when the current token expires.
    """
    def __init__(self, client_id, client_secret, token_url):
        """
        Initializes the client and fetches the first access token.

        Args:
            client_id: OAuth2 client identifier.
            client_secret: OAuth2 client secret.
            token_url: Full URL to the OAuth2 token endpoint.

        Raises:
            requests.HTTPError: If the initial token request fails.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._token_data = None
        self._expires_at = None

        self._fetch_token()

    def _fetch_token(self) -> None:
        """
        Fetches a new access token from the OAuth2 server and stores it.

        Uses client credentials flow with application/x-www-form-urlencoded content type.
        Updates both the token data and expiration timestamp.

        Raises:
            requests.HTTPError: If the token request fails (4xx/5xx status).
            ValueError: If the token response is malformed.
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(self._token_url, data=payload, headers=headers)
        response.raise_for_status()

        token_info = response.json()
        self._token_data = {
            "token": token_info["access_token"],
            "metadata": token_info
        }

        self._expires_at = time.time() + token_info["expires_in"]
    
    def get_token(self) -> str:
        """
        Retrieves a valid access token, automatically refreshing if expired.

        Returns:
            str: The current valid access token.

        Note:
            Prints a message to stdout when refreshing expired tokens. In production,
            consider using logging instead.

        Example:
            >>> client = DF_Client("id", "secret", "https://api.example.com/token")
            >>> token = client.get_token()  # Gets token, auto-refreshes if needed
        """
        if not self._token_data or time.time() >= self._expires_at:
            print("Token expired. Refreshing...")
            self._fetch_token()
        return self._token_data["token"]