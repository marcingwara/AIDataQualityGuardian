from datetime import datetime
from src.utils.logger import logger


class ReportBuilder:
    """
    Converts raw Data Quality issues into a structured, readable report.

    Input:
    [
        {
            "dashboard": "Sales Overview",
            "issues": [
                {
                    "metric": "Revenue",
                    "issue": "Sudden spike detected",
                    "details": "Value 5000 is > 3x above mean (1100.0)"
                }
            ]
        }
    ]

    Output (Slack-friendly text):
    🚨 Data Quality Report — 2025-02-27

    🔴 Sales Overview
        • [Revenue] Sudden spike detected — Value 5000 is > 3x above mean (1100.0)
    """

    @staticmethod
    def build(all_issues: list) -> str:

        if not all_issues:
            return "✅ All dashboards are healthy. No data quality issues detected."

        report_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Header
        report_lines.append(f"🚨 *Data Quality Report — {timestamp}*")
        report_lines.append("")

        for entry in all_issues:
            dashboard_name = entry.get("dashboard", "Unknown Dashboard")
            issues = entry.get("issues", [])

            # Dashboard Header
            report_lines.append(f"🔴 *{dashboard_name}*")

            for issue in issues:
                metric = issue.get("metric", "Unknown Metric")
                issue_name = issue.get("issue", "Unknown Issue")
                details = issue.get("details", "")

                report_lines.append(f"   • [{metric}] *{issue_name}* — {details}")

            report_lines.append("")  # blank line between dashboards

        final_report = "\n".join(report_lines)

        logger.info("Report built successfully.")
        return final_report