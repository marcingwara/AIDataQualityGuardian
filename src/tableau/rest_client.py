import os
import requests
import xmltodict
from dotenv import load_dotenv
from src.utils.logger import logger
from io import StringIO
import csv

# Load .env
load_dotenv()


class TableauRestClient:
    """
    Tableau Cloud REST API client (supports XML + CSV responses)
    """

    def __init__(self):
        self.server = os.getenv("TABLEAU_CLOUD_URL")
        self.site_content_url = os.getenv("TABLEAU_SITE_ID")
        self.token_name = os.getenv("TABLEAU_TOKEN_NAME")
        self.token_secret = os.getenv("TABLEAU_TOKEN_SECRET")

        if not all([self.server, self.site_content_url, self.token_name, self.token_secret]):
            logger.error("❌ Tableau API not fully configured in .env")
            self.enabled = False
            return

        self.enabled = True
        self.api_version = "3.22"
        self.sign_in_url = f"{self.server}/api/{self.api_version}/auth/signin"

        self.token = None
        self.tableau_site_id = None  # GUID returned by signin

        self._sign_in()

    # --------------------------------------------------------------------
    # SAFE PARSER (XML → dict)
    # --------------------------------------------------------------------
    def _safe_parse(self, response):
        text = response.text.strip()
        if not text:
            return None

        try:
            # Try JSON first
            return response.json()
        except:
            pass

        # Try XML
        try:
            return xmltodict.parse(text)
        except Exception as e:
            logger.error(f"❌ XML parse error: {e}")
            return None

    # --------------------------------------------------------------------
    # SIGN IN
    # --------------------------------------------------------------------
    def _sign_in(self):
        logger.info("🔐 Signing in to Tableau Cloud API...")

        payload = {
            "credentials": {
                "personalAccessTokenName": self.token_name,
                "personalAccessTokenSecret": self.token_secret,
                "site": {"contentUrl": self.site_content_url}
            }
        }

        response = requests.post(
            self.sign_in_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        # Debug raw response
        print("\n========== DEBUG RAW RESPONSE ==========")
        print(response.text)
        print("========================================\n")

        if response.status_code != 200:
            logger.error(f"❌ Authentication failed: {response.text}")
            self.enabled = False
            return

        parsed = self._safe_parse(response)
        creds = parsed.get("credentials") or parsed.get("tsResponse", {}).get("credentials")

        if not creds:
            logger.error("❌ Could not locate credentials in login response.")
            self.enabled = False
            return

        self.token = creds["token"]
        self.tableau_site_id = creds["site"]["id"]

        logger.info("🔥 Successfully authenticated with Tableau Cloud.")

    # --------------------------------------------------------------------
    # HEADERS
    # --------------------------------------------------------------------
    def _headers(self):
        return {
            "X-Tableau-Auth": self.token,
            "Accept": "application/json"
        }

    # --------------------------------------------------------------------
    # GET WORKBOOKS
    # --------------------------------------------------------------------
    def get_workbooks(self):
        url = f"{self.server}/api/{self.api_version}/sites/{self.tableau_site_id}/workbooks"

        response = requests.get(url, headers=self._headers())
        parsed = self._safe_parse(response)

        if not parsed:
            logger.error("❌ Failed to parse workbooks XML")
            return []

        # XML path: tsResponse → workbooks → workbook
        workbooks = (
            parsed.get("tsResponse", {})
            .get("workbooks", {})
            .get("workbook", [])
        )

        # Ensure list
        if isinstance(workbooks, dict):
            workbooks = [workbooks]

        return workbooks

    # --------------------------------------------------------------------
    # GET VIEWS
    # --------------------------------------------------------------------
    def get_views(self):
        """Fetch all views (dashboards) on the site."""
        url = f"{self.server}/api/{self.api_version}/sites/{self.tableau_site_id}/views"

        response = requests.get(url, headers=self._headers())

        # Debug raw
        print("\n========== VIEWS RAW RESPONSE ==========")
        print(response.text[:5000])
        print("========================================\n")

        # 1. Try JSON first (your API uses JSON)
        try:
            data = response.json()
            if "views" in data and "view" in data["views"]:
                views = data["views"]["view"]
                logger.info(f"📊 Parsed {len(views)} views from JSON.")
                return views
        except Exception:
            pass

        # 2. Fallback to XML parsing
        parsed = self._safe_parse(response)
        if parsed:
            candidates = [
                parsed.get("tsResponse", {}).get("views", {}).get("view"),
                parsed.get("views", {}).get("view"),
            ]
            for c in candidates:
                if isinstance(c, list):
                    logger.info(f"📊 Parsed {len(c)} views from XML.")
                    return c

        # If nothing matched
        logger.error("❌ Could not extract views from Tableau response.")
        return []

    # --------------------------------------------------------------------
    # GET VIEW DATA (CSV)
    # --------------------------------------------------------------------
    def get_view_data(self, view_id):
        url = f"{self.server}/api/{self.api_version}/sites/{self.tableau_site_id}/views/{view_id}/data?includeAll=true"

        response = requests.get(url, headers=self._headers())

        if response.status_code != 200:
            logger.error(f"❌ Failed to fetch data for view {view_id}: {response.text}")
            return None

        text = response.text.strip()

        # Detect CSV
        if "," in text and "\n" in text:
            try:
                reader = csv.DictReader(StringIO(text))
                rows = list(reader)
                print("DEBUG get_view_data TYPE:", type(response.text))
                print("DEBUG get_view_data CONTENT:", response.text[:500])
                return text
            except Exception as e:
                logger.error(f"❌ CSV parse error: {e}")
                return None

        logger.error("❌ Summary data was not CSV")
        return None