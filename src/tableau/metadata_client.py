import requests
from src.utils.logger import logger


class MetadataClient:
    """
    Handles communication with the Tableau Metadata API using GraphQL.
    """

    def __init__(self, server, site, token_name, token_secret):
        self.server = server
        self.site = site
        self.token_name = token_name
        self.token_secret = token_secret

        self.auth_token = None
        self.site_id = None

    # ---------------------------
    #   Authentication
    # ---------------------------
    def authenticate(self):
        """
        Authenticate using a Personal Access Token and retrieve the auth token + site ID.
        """
        url = f"{self.server}/api/3.19/auth/signin"
        payload = {
            "credentials": {
                "personalAccessTokenName": self.token_name,
                "personalAccessTokenSecret": self.token_secret,
                "site": {"contentUrl": self.site}
            }
        }

        logger.info("Authenticating with Tableau...")

        response = requests.post(url, json=payload)
        if response.status_code != 200:
            logger.error(f"Authentication failed: {response.text}")
            raise Exception("Tableau authentication failed")

        data = response.json()
        self.auth_token = data["credentials"]["token"]
        self.site_id = data["credentials"]["site"]["id"]

        logger.info("Authentication successful.")

    # ---------------------------
    #   GraphQL Query Runner
    # ---------------------------
    def run_graphql_query(self, query):
        """
        Executes a GraphQL query against the Tableau Metadata API.
        """

        if not self.auth_token:
            self.authenticate()

        url = f"{self.server}/api/metadata/graphql"

        headers = {
            "Content-Type": "application/json",
            "X-Tableau-Auth": self.auth_token
        }

        response = requests.post(url, json={"query": query}, headers=headers)

        if response.status_code != 200:
            logger.error(f"Metadata API error: {response.text}")
            raise Exception("GraphQL query failed")

        return response.json()

    # ---------------------------
    #   Fetch Dashboards
    # ---------------------------
    def get_dashboards(self):
        """
        Fetches a list of dashboards from Tableau via GraphQL.
        """
        query = """
        {
          dashboards {
            id
            name
            workbook {
              name
            }
            sheets {
              id
              name
            }
          }
        }
        """

        logger.info("Running Metadata API query for dashboards...")
        data = self.run_graphql_query(query)

        dashboards = data.get("data", {}).get("dashboards", [])

        logger.info(f"Metadata API returned {len(dashboards)} dashboards.")
        return dashboards

    # ---------------------------
    #   Fetch Metrics (KPI)
    # ---------------------------
    def get_metrics_for_dashboard(self, dashboard_id):
        """
        Fetches metrics/KPI values for a dashboard.
        (Example GraphQL query – may require adjustment for real data sources)
        """

        query = f"""
        {{
          dashboard(id: "{dashboard_id}") {{
            name
            worksheets {{
              name
              dataSources {{
                fields {{
                  name
                  dataType
                }}
              }}
            }}
          }}
        }}
        """

        logger.info(f"Fetching metrics for dashboard: {dashboard_id}")

        data = self.run_graphql_query(query)
        return data.get("data", {})