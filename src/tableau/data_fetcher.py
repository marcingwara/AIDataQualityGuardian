from src.utils.logger import logger
from src.tableau.metadata_client import MetadataClient
from src.tableau.parsers.metrics_parser import MetricsParser


class DataFetcher:
    """
    High-level class that combines Metadata API + parsing logic
    to return clean data for Data Quality checks.
    """

    def __init__(self, metadata_client: MetadataClient):
        self.metadata_client = metadata_client
        self.metrics_parser = MetricsParser()

    # ---------------------------
    # Fetch dashboards
    # ---------------------------
    def get_dashboards(self):
        """
        Returns all dashboards from Tableau Metadata API.
        Each dashboard entry includes:
        - id
        - name
        - sheets
        - workbook name
        """
        try:
            dashboards = self.metadata_client.get_dashboards()
            return dashboards
        except Exception as e:
            logger.error(f"Error fetching dashboards: {e}")
            return []

    # ---------------------------
    # Fetch KPI / metrics
    # ---------------------------
    def get_metrics_for_dashboard(self, dashboard):
        """
        Extracts all KPI/metrics from a dashboard using:
        - MetadataClient (GraphQL)
        - MetricsParser (parsing the response)

        Returns cleaned structure:
        {
            "Revenue": [1500, 1600, 1480],
            "Orders": [85, 92, 80]
        }
        """

        dashboard_id = dashboard.get("id")
        name = dashboard.get("name")

        logger.info(f"Fetching KPI for dashboard '{name}' (ID: {dashboard_id})")

        # Step 1 → pobierz raw metadane GraphQL
        try:
            raw_data = self.metadata_client.get_metrics_for_dashboard(dashboard_id)
        except Exception as e:
            logger.error(f"Failed to fetch metrics for {name}: {e}")
            return {}

        # Step 2 → przetwórz metadane i wyciągnij KPI
        try:
            metrics = self.metrics_parser.extract_metrics(raw_data)
            logger.info(f"Extracted {len(metrics)} metrics from {name}")
            return metrics
        except Exception as e:
            logger.error(f"Failed to parse metrics for {name}: {e}")
            return {}