import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
import requests
import time
import os
from environs import env
from google.api_core import exceptions
from google.cloud import secretmanager

logging.basicConfig(
	level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("FT_Client")

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
		self._token_data = None
		self._expires_in = None
		self._secrets_cache = {}
		self._client_id = None
		self._client_secret = None
		self._token_url = None

		env.read_env()

		self._client_id = self._get_secret("CLIENT_ID")
		self._client_secret = self._get_secret("CLIENT_SECRET")
		self._token_url = env.str("TOKEN_URL")

		logger.info("Initializing FT_Client...")
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
			logger.warning("Token expired or missing. Refreshing...")
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

			logger.debug(f"Requesting new token from {self._token_url}")
			response = requests.post(self._token_url, data=payload, headers=headers)
			response.raise_for_status()

			token_info = response.json()
			self._token_data = {
				"token": token_info["access_token"],
				"metadata": token_info,
			}

			self._expires_in = time.time() + token_info["expires_in"]
			logger.info(
				"Successfully fetched new token. "
				f"Expires in {token_info['expires_in']} seconds."
			)
		except requests.RequestException as e:
			logger.error(f"Token fetch failed: {str(e)}", exc_info=True)
			raise
		

	def _on_cloud(self):
		return os.getenv("K_SERVICE") is not None
	
	def	_get_secret(self, secret_id: str, version:str = "latest") -> str:
			cache_key = f"{secret_id}_{version}"
			
			if cache_key in self._secrets_cache:
				logger.debug(f"Cache hit for secret: {cache_key}")
				return self._secrets_cache[cache_key]
			
			secret_value = None

			if self._on_cloud():
				logger.info(f"Trying to fetch secret '{secret_id}' from Secret Manager.")

				try:
					project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
					if not project_id:
						project_id = requests.get(
							'http://metadata.google.internal/computeMetadata/v1/project/project-id',
							headers={
								'Metadata-Flavor': 'Google'
							}
						).text
					
					client = secretmanager.SecretManagerServiceClient()
					name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
					response = client.access_secret_version(request={"name": name})
					secret_value = response.payload.data.decode("UTF-8")

					logger.info(f"Successfully fetched secret '{secret_id}' from Secret Manager!")
				
				except exceptions.NotFound:
					logger.error(f"Secret '{secret_id}' not found.")
				except exceptions.PermissionDenied:
					logger.error(f"Permission denied for secret '{secret_id}'. Check IAM Permission for the Service Account.")
				except Exception as e:
					logger.warning(f"Unexpected error fetching secret from SM: {str(e)}. Falling back to local env.")
			
			if secret_value is None:
				logger.info(f"Executin' local fetch for secret '{secret_id}'...")

				secret_value = env.str(secret_id, None)
				if secret_value is None:
					err_msg = (
						f"Secret '{secret_id}' could not be found."
						f"Checked: {'Secret Manager' if self._on_cloud() else ''}"
						f"local environment variables, and .env file..."
					)
					
					logger.error(err_msg)
					raise ValueError(err_msg)
				else:
					logger.info(f"Found secret '{secret_id}' in local environment.")
			
			self._secrets_cache[cache_key] = secret_value
			return secret_value