import os
import requests
from src.utils.logger import logger


class TableauMetadataClient:
    """
    Tableau Cloud Metadata API Client (GraphQL)
    Allows retrieving:
    - workbooks
    - dashboards (views)
    - data sources
    - fields with data types
    - lineage (upstream/downstream)
    """

    def __init__(self, auth_token=None, site_id=None):
        self.server = os.getenv("TABLEAU_CLOUD_URL")
        self.api_version = "3.22"

        # Auth token & site GUID from REST client
        self.token = auth_token
        self.site_id = site_id

        if not self.token or not self.site_id:
            logger.error("❌ Metadata API requires a valid REST API session.")
            self.enabled = False
            return

        self.enabled = True
        self.url = f"{self.server}/api/metadata/graphql"

    # ------------------------------------------------------------
    # GraphQL QUERY EXECUTION
    # ------------------------------------------------------------
    def _query(self, query: str, variables: dict = None):
        if not self.enabled:
            logger.warning("Metadata API disabled — skipping query.")
            return None

        headers = {
            "Content-Type": "application/json",
            "X-Tableau-Auth": self.token
        }

        payload = {
            "query": query,
            "variables": variables or {}
        }

        response = requests.post(self.url, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error(f"❌ GraphQL error: {response.text}")
            return None

        return response.json()

    # ------------------------------------------------------------
    # GET DASHBOARD METADATA (FIELDS + DATASOURCES)
    # ------------------------------------------------------------
    def get_dashboard_metadata(self, workbook_id: str):
        """
        Retrieves dashboard → worksheets → fields → types → lineage.
        """

        logger.info(f"🔍 Fetching metadata for workbook {workbook_id}...")

        query = """
        query GetWorkbookMetadata($id: ID!) {
          workbook(id: $id) {
            name
            sheets {
              name
              fields {
                name
                dataType
                role
                isHidden
                upstreamTables {
                  name
                  fullName
                }
              }
            }
            upstreamDatasources {
              name
              connectionType
            }
          }
        }
        """

        result = self._query(query, {"id": workbook_id})

        if not result:
            return None

        return result["data"]["workbook"]

    # ------------------------------------------------------------
    # GET DATASOURCE FIELDS
    # ------------------------------------------------------------
    def get_datasource_fields(self, datasource_id: str):
        """
        Returns all fields for a datasource.
        """
        logger.info(f"📘 Fetching datasource fields for {datasource_id}...")

        query = """
        query GetDatasourceFields($id: ID!) {
          datasource(id: $id) {
            name
            fields {
              name
              dataType
              role
              isHidden
            }
          }
        }
        """

        result = self._query(query, {"id": datasource_id})

        if not result:
            return None

        return result["data"]["datasource"]

    # ------------------------------------------------------------
    # GET FIELD LINEAGE (UPSTREAM PATH)
    # ------------------------------------------------------------
    def get_field_lineage(self, field_id: str):
        """
        Return lineage for a specific field.
        """
        logger.info(f"🔗 Fetching lineage for field {field_id}...")

        query = """
        query GetFieldLineage($id: ID!) {
          field(id: $id) {
            name
            dataType
            role
            upstreamFields {
              name
              dataType
              upstreamTables {
                name
                fullName
              }
            }
          }
        }
        """

        result = self._query(query, {"id": field_id})

        if not result:
            return None

        return result["data"]["field"]

    # ------------------------------------------------------------
    # GET WORKBOOK LIST WITH METADATA SUPPORT
    # ------------------------------------------------------------
    def get_all_workbook_metadata(self):
        """
        Returns all workbooks + high-level metadata.
        """

        logger.info("📚 Fetching list of workbooks with metadata...")

        query = """
        {
          workbooks {
            id
            name
            projectName
            owner {
              name
            }
          }
        }
        """

        result = self._query(query)

        if not result:
            return []

        return result["data"]["workbooks"]
        # ------------------------------------------------------------
    # GET VIEW METADATA
    # ------------------------------------------------------------
    def get_view_metadata(self, view_id: str):
        """
        Retrieves metadata for a VIEW (dashboard or sheet):
        - view name
        - workbook
        - fields
        - data types
        - lineage
        """

        logger.info(f"🧩 Fetching metadata for VIEW {view_id}...")

        query = """
        query GetViewFields($id: ID!) {
          view(id: $id) {
            id
            name
            workbook {
              id
              name
            }
            fields {
              id
              name
              dataType
              role
              isHidden
              upstreamTables {
                id
                name
                fullName
              }
            }
          }
        }
        """

        result = self._query(query, {"id": view_id})

        if not result:
            logger.error(f"❌ No metadata returned for view {view_id}")
            return None

        if "data" not in result or "view" not in result["data"]:
            logger.error(f"❌ GraphQL returned invalid structure for view {view_id}: {result}")
            return None

        return result["data"]["view"]