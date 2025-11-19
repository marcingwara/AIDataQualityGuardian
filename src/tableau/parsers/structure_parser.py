from src.utils.logger import logger


class StructureParser:
    """
    Parses Tableau dashboard structure from GraphQL metadata.

    Returns a clean structure describing:
    - dashboard -> worksheets
    - worksheets -> fields
    - fields -> data types
    - data sources used in each sheet
    """

    def parse(self, raw_data):
        """
        Input (GraphQL):
        {
          "dashboard": {
            "name": "Sales Overview",
            "worksheets": [
              {
                "name": "Sheet 1",
                "dataSources": [
                  {
                    "name": "Sales DS",
                    "fields": [
                      {"name": "Revenue", "dataType": "integer"},
                      {"name": "Region", "dataType": "string"}
                    ]
                  }
                ]
              }
            ]
          }
        }

        Output (cleaned):
        {
            "dashboard_name": "Sales Overview",
            "worksheets": {
                "Sheet 1": {
                    "data_sources": {
                        "Sales DS": {
                            "fields": {
                                "Revenue": "integer",
                                "Region": "string"
                            }
                        }
                    }
                }
            }
        }
        """

        try:
            dashboard = raw_data.get("dashboard", {})
            dashboard_name = dashboard.get("name", "Unnamed Dashboard")

            cleaned_structure = {
                "dashboard_name": dashboard_name,
                "worksheets": {}
            }

            worksheets = dashboard.get("worksheets", [])

            for ws in worksheets:
                ws_name = ws.get("name", "Unnamed Sheet")
                cleaned_structure["worksheets"][ws_name] = {
                    "data_sources": {}
                }

                ds_list = ws.get("dataSources", [])

                for ds in ds_list:
                    ds_name = ds.get("name", "Unnamed Data Source")
                    cleaned_structure["worksheets"][ws_name]["data_sources"][ds_name] = {
                        "fields": {}
                    }

                    fields = ds.get("fields", [])

                    for field in fields:
                        field_name = field.get("name", "Unnamed Field")
                        field_type = field.get("dataType", "unknown")

                        cleaned_structure["worksheets"][ws_name]["data_sources"][ds_name]["fields"][field_name] = field_type

            logger.info(f"Parsed structure for dashboard '{dashboard_name}'")
            return cleaned_structure

        except Exception as e:
            logger.error(f"Structure parsing failed: {e}")
            return {}