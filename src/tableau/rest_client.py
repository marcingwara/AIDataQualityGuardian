import requests
from src.utils.logger import logger


class RestClient:
    """
    Lightweight REST API client for Tableau.
    Handles authentication and standard HTTP calls.
    """

    API_VERSION = "3.19"  # możesz zmienić na najnowszą

    def __init__(self, server, site, token_name, token_secret):
        self.server = server
        self.site = site
        self.token_name = token_name
        self.token_secret = token_secret

        self.auth_token = None
        self.site_id = None

    # ---------------------------
    # AUTHENTICATION
    # ---------------------------
    def authenticate(self):
        """
        Sign in to Tableau using a Personal Access Token (PAT).
        """
        url = f"{self.server}/api/{self.API_VERSION}/auth/signin"

        payload = {
            "credentials": {
                "personalAccessTokenName": self.token_name,
                "personalAccessTokenSecret": self.token_secret,
                "site": {"contentUrl": self.site}
            }
        }

        logger.info("Authenticating with Tableau REST API...")

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            logger.error(f"REST auth failed: {response.text}")
            raise Exception("REST API authentication failed")

        data = response.json()
        self.auth_token = data["credentials"]["token"]
        self.site_id = data["credentials"]["site"]["id"]

        logger.info("REST authentication successful.")

    # ---------------------------
    # GENERIC REQUEST METHOD
    # ---------------------------
    def _request(self, method, endpoint, **kwargs):
        """
        Internal method to call Tableau REST API.
        Automatically re-authenticates when needed.
        """

        if not self.auth_token:
            self.authenticate()

        url = f"{self.server}/api/{self.API_VERSION}/{endpoint}"

        headers = kwargs.pop("headers", {})
        headers["X-Tableau-Auth"] = self.auth_token

        response = requests.request(method, url, headers=headers, **kwargs)

        # Token may expire → try re-authentication
        if response.status_code == 401:
            logger.warning("Auth token expired. Re-authenticating...")
            self.authenticate()
            headers["X-Tableau-Auth"] = self.auth_token
            response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code not in [200, 201, 204]:
            logger.error(f"REST request failed: {response.text}")
            raise Exception(f"REST API error: {response.status_code}")

        return response

    # ---------------------------
    # PUBLIC METHODS (for other modules)
    # ---------------------------
    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, json=None, data=None, files=None):
        return self._request("POST", endpoint, json=json, data=data, files=files)

    def put(self, endpoint, json=None):
        return self._request("PUT", endpoint, json=json)

    def delete(self, endpoint):
        return self._request("DELETE", endpoint)