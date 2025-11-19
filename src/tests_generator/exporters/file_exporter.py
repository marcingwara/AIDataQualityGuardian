import os
from src.utils.logger import logger


class FileExporter:
    """
    Saves generated test cases into Python .py files in a defined output directory.

    Usage:
        exporter = FileExporter("generated_tests/")
        exporter.export_tests(tests_dict)
    """

    def __init__(self, output_dir="generated_tests"):
        self.output_dir = output_dir

        # Create folder if missing
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"FileExporter: output directory ready: {self.output_dir}")

    def export_tests(self, tests_by_dashboard: dict):
        """
        tests_by_dashboard is dict:
        {
            "Sales Overview": "def test_sales_revenue():\n   ...",
            "Marketing Dashboard": "def test_marketing_visits():\n   ..."
        }
        """

        for dashboard_name, test_code in tests_by_dashboard.items():

            safe_name = dashboard_name.lower().replace(" ", "_").replace("/", "_")
            file_path = os.path.join(self.output_dir, f"{safe_name}_tests.py")

            try:
                with open(file_path, "w") as f:
                    f.write("# Auto-generated test suite\n")
                    f.write("# Do not edit manually\n\n")
                    f.write(test_code)

                logger.info(f"FileExporter: wrote test file → {file_path}")

            except Exception as e:
                logger.error(f"Failed to write test file for {dashboard_name}: {e}")