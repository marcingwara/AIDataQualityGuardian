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
from src.dq.report_builder import ReportBuilder

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
# PROCESS SINGLE DASHBOARD
# =====================================================================================

def process_dashboard(name, metrics, expected_ranges):
    logger.info(f"Processing dashboard: {name}")

    # 1. Rule-based checks
    rules = QualityRules()
    rule_issues = rules.check_all(metrics)

    # 2. Anomaly detection
    detector = AnomalyDetector()
    anomaly_issues = detector.detect(metrics)

    # 3. Additional validation
    validators = Validators()
    validation_issues = validators.validate(metrics, expected_ranges)

    # Combine issues
    all_issues = rule_issues + anomaly_issues + validation_issues

    # 4. AI insights
    ai = AIAnalyzer()
    entry = {"dashboard": name, "issues": all_issues}
    entry = ai.analyze_all([entry])[0]

    # 5. Score
    scorer = ScoreCalculator()
    entry["score"] = scorer.calculate_score(entry["issues"])

    return entry


# =====================================================================================
# MAIN PIPELINE
# =====================================================================================

def main():
    logger.info("🚀 Starting AIDataQualityGuardian")

    results = []

    # ---------------------------------------------------------------------------------
    # 1. FETCH DATA
    # ---------------------------------------------------------------------------------
    if USE_TABLEAU_API:
        logger.info("🌐 Using Tableau Cloud API...")

        rest = TableauRestClient()

        if not rest.enabled:
            logger.error("❌ Tableau API login failed → using MOCK data instead")
        else:
            metadata = TableauMetadataClient(
                auth_token=rest.token,
                site_id=rest.tableau_site_id
            )

            fetcher = DataFetcher(rest, metadata)

            dashboards = fetcher.fetch_all_dashboard_metrics()

            if dashboards:
                logger.info(f"📊 Loaded {len(dashboards)} dashboards from Tableau Cloud.")

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
                USE_MOCK = True

    if not USE_TABLEAU_API:
        logger.warning("⚠️ Using MOCK DATA (Tableau API disabled or failed)")
        for d in MOCK_DASHBOARDS:
            results.append(process_dashboard(d["dashboard"], d["metrics"], d["expected_ranges"]))

    # ---------------------------------------------------------------------------------
    # 2. LOG RESULTS
    # ---------------------------------------------------------------------------------
    logger.info("All dashboards processed.")
    logger.info(Helper.to_pretty_json(results))

    # ---------------------------------------------------------------------------------
    # 3. SLACK
    # ---------------------------------------------------------------------------------
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        slack = SlackNotifier(slack_url)
        blocks = MessageTemplates.build_block_report(results)
        slack.send_blocks(blocks)
    else:
        logger.warning("Slack webhook not configured.")

    # ---------------------------------------------------------------------------------
    # 4. EMAIL
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
            logger.error("Email sending failed: " + str(e))
    else:
        logger.warning("Email SMTP not configured.")

    # ---------------------------------------------------------------------------------
    # 5. JIRA
    # ---------------------------------------------------------------------------------
    jira = JiraExporter()
    for d in results:
        issue_url = jira.create_issue(d["dashboard"], d["issues"])
        if issue_url:
            logger.info(f"JIRA Ticket created: {issue_url}")
            if slack_url:
                slack.send_text(f"🐞 JIRA Ticket created: {issue_url}")

    # ---------------------------------------------------------------------------------
    # 6. GENERATE TESTS
    # ---------------------------------------------------------------------------------
    test_builder = TestBuilder()
    tests = test_builder.build_tests(results)
    exporter = FileExporter("generated_tests")
    exporter.export_tests(tests)

    logger.info("Test generation completed.")
    logger.info("🎉 AIDataQualityGuardian run complete.")


# =====================================================================================
# ENTRYPOINT
# =====================================================================================

if __name__ == "__main__":
    main()