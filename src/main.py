# =====================================================================================
# LOAD .ENV BEFORE ANY IMPORTS (THIS FIXES THE OPENAI FALLBACK ISSUE)
# =====================================================================================

from dotenv import load_dotenv
load_dotenv()   # <---- MUST BE FIRST LINE

import os
from src.utils.logger import logger
from src.utils.helper import Helper

# Tableau API clients
from src.tableau.rest_client import TableauRestClient
from src.tableau.metadata_client import TableauMetadataClient

# Data fetching & transformation
from src.tableau.data_fetcher import DataFetcher

# DQ modules
from src.dq.quality_rules import QualityRules
from src.dq.anomaly_detector import AnomalyDetector
from src.dq.ai_analyzer import AIAnalyzer
from src.dq.score_calculator import ScoreCalculator
from src.dq.validators import Validators

# Alerts
from src.alerts.slack_notifier import SlackNotifier
from src.alerts.email_notifier import EmailNotifier
from src.alerts.message_templates import MessageTemplates

# Test generation
from src.tests_generator.test_builder import TestBuilder
from src.tests_generator.exporters.file_exporter import FileExporter

# JIRA
from src.tests_generator.exporters.jira_exporter import JiraExporter


# =====================================================================================
# CONFIG
# =====================================================================================

USE_TABLEAU_API = os.getenv("USE_TABLEAU_API", "False").lower() == "true"


# =====================================================================================
# MOCK FALLBACK
# =====================================================================================

MOCK_DASHBOARDS = [
    {
        "dashboard": "Sales Overview",
        "metrics": {
            "Revenue": [1000, 1050, 1020, 5200],
            "Orders": [82, 80, 81, None],
            "Margin": [25, 25, 25, 25],
        },
        "expected_ranges": {
            "Revenue": (900, 2000),
            "Orders": (50, 150),
            "Margin": (10, 50)
        }
    },
    {
        "dashboard": "Marketing Performance",
        "metrics": {
            "SiteVisits": [300, 310, 305, 0],
            "Conversions": [5, 7, -2, 8],
            "Cost": [200, 180, 500, 210],
        },
        "expected_ranges": {
            "SiteVisits": (200, 1000),
            "Conversions": (0, 50),
            "Cost": (100, 300)
        }
    }
]


# =====================================================================================
# PROCESS ONE DASHBOARD
# =====================================================================================

def process_dashboard(name, metrics, expected_ranges):
    logger.info(f"Processing dashboard: {name}")

    # Rule-based checks
    rule_issues = QualityRules().check_all(metrics)

    # Anomaly detection
    anomaly_issues = AnomalyDetector().detect(metrics)

    # Validation vs expected ranges
    validation_issues = Validators().validate(metrics, expected_ranges)

    # Merge
    all_issues = rule_issues + anomaly_issues + validation_issues

    # AI insights
    ai = AIAnalyzer()
    entry = {"dashboard": name, "issues": all_issues}
    entry = ai.analyze_all([entry])[0]

    # Score
    entry["score"] = ScoreCalculator().calculate_score(entry["issues"])

    return entry


# =====================================================================================
# MAIN PIPELINE
# =====================================================================================

def main():
    logger.info("🚀 Starting AIDataQualityGuardian")

    results = []

    # ---------------------------------------------------------------------------------
    # 1. FETCH DATA (Tableau or Mock)
    # ---------------------------------------------------------------------------------

    if USE_TABLEAU_API:
        logger.info("🌐 Using Tableau Cloud API...")

        rest = TableauRestClient()

        if rest.enabled:
            metadata = TableauMetadataClient(
                auth_token=rest.token,
                site_id=rest.tableau_site_id
            )

            fetcher = DataFetcher(rest, metadata)
            dashboards = fetcher.fetch_all_dashboard_metrics()

            if dashboards:
                for dash in dashboards:
                    results.append(
                        process_dashboard(
                            name=dash["dashboard"],
                            metrics=dash["metrics"],
                            expected_ranges=dash["expected_ranges"]
                        )
                    )
            else:
                logger.error("❌ No dashboards available → using MOCK data")
        else:
            logger.error("❌ REST API disabled → using MOCK data")
            USE_MOCK = True

    if not USE_TABLEAU_API:
        logger.warning("⚠️ Using MOCK DATA")
        for d in MOCK_DASHBOARDS:
            results.append(process_dashboard(d["dashboard"], d["metrics"], d["expected_ranges"]))

    # ---------------------------------------------------------------------------------
    # 2. Log results
    # ---------------------------------------------------------------------------------

    logger.info("All dashboards processed.")
    logger.info(Helper.to_pretty_json(results))

    # ---------------------------------------------------------------------------------
    # 3. Slack Alerts
    # ---------------------------------------------------------------------------------

    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        slack = SlackNotifier(slack_url)
        blocks = MessageTemplates.build_block_report(results)
        slack.send_blocks(blocks)

    # ---------------------------------------------------------------------------------
    # 4. Email Alerts
    # ---------------------------------------------------------------------------------

    smtp_host = os.getenv("SMTP_HOST")
    if smtp_host:
        try:
            emailer = EmailNotifier(
                smtp_host=smtp_host,
                smtp_port=int(os.getenv("SMTP_PORT", 587)),
                username=os.getenv("SMTP_USERNAME"),
                password=os.getenv("SMTP_PASSWORD"),
                from_email=os.getenv("EMAIL_FROM"),
                to_emails=os.getenv("EMAIL_TO")
            )
            html = "<h2>Data Quality Report</h2>" + Helper.to_pretty_json(results).replace("\n", "<br>")
            emailer.send_report("Data Quality Report", html, is_html=True)
        except Exception as e:
            logger.error(f"Email sending failed: {e}")

    # ---------------------------------------------------------------------------------
    # 5. JIRA Tickets
    # ---------------------------------------------------------------------------------

    jira = JiraExporter()
    for d in results:
        issue_url = jira.create_issue(d["dashboard"], d["issues"])
        if issue_url and slack_url:
            SlackNotifier(slack_url).send_text(f"🐞 JIRA Ticket created: {issue_url}")

    # ---------------------------------------------------------------------------------
    # 6. Generate Tests
    # ---------------------------------------------------------------------------------

    tests = TestBuilder().build_tests(results)
    FileExporter("generated_tests").export_tests(tests)

    logger.info("Test generation completed.")
    logger.info("🎉 AIDataQualityGuardian run complete.")

# =====================================================================================
# ENTRYPOINT
# =====================================================================================

if __name__ == "__main__":
    main()