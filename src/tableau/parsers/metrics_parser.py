from src.utils.logger import logger


class MetricsParser:
    """
    Extracts KPI values and metric names from Tableau Metadata GraphQL responses.
    The output format is simple and ready for Data Quality checks:

    {
        "Revenue": [1200, 1300, 1100],
        "Orders": [85, 92, 88]
    }
    """

    def extract_metrics(self, raw_data):
        """
        Processes raw GraphQL data and extracts KPIs.

        raw_data structure looks like:
        {
          "dashboard": {
            "name": "...",
            "worksheets": [
              {
                "name": "...",
                "dataSources": [
                  {
                    "fields": [
                       {"name": "Revenue", "dataType": "integer"},
                       {"name": "Orders", "dataType": "integer"},
                       ...
                    ]
                  }
                ]
              }
            ]
          }
        }
        """

        metrics = {}

        try:
            dashboard = raw_data.get("dashboard", {})
            worksheets = dashboard.get("worksheets", [])

            for ws in worksheets:
                ws_name = ws.get("name", "Unnamed sheet")
                data_sources = ws.get("dataSources", [])

                for ds in data_sources:
                    fields = ds.get("fields", [])

                    for field in fields:
                        field_name = field.get("name")
                        field_type = field.get("dataType")

                        # We treat numeric fields as KPI
                        if field_type in ["integer", "float", "double", "real", "number"]:
                            # For MVP: simulate simple metric values
                            # (In real usage, add REST data queries here)
                            metrics[field_name] = metrics.get(field_name, [100, 110, 105])

            logger.info(f"Extracted metrics: {list(metrics.keys())}")
            return metrics

        except Exception as e:
            logger.error(f"Metrics parsing failed: {e}")
            return {}