from src.utils.logger import logger
from src.utils.helper import Helper

# DQ modules
from src.dq.quality_rules import QualityRules
from src.dq.anomaly_detector import AnomalyDetector
from src.dq.ai_analyzer import AIAnalyzer
from src.dq.score_calculator import ScoreCalculator
from src.dq.validators import Validators

# Reports
from src.dq.report_builder import ReportBuilder

# Alerts
from src.alerts.slack_notifier import SlackNotifier
from src.alerts.email_notifier import EmailNotifier
from src.alerts.message_templates import MessageTemplates

# Test generation
from src.tests_generator.test_builder import TestBuilder
from src.tests_generator.exporters.file_exporter import FileExporter

# 👉 JIRA integration (now active)
from src.tests_generator.exporters.jira_exporter import JiraExporter

import os


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


def process_dashboard(dashboard_data):
    dashboard_name = dashboard_data["dashboard"]
    metrics = dashboard_data["metrics"]
    expected_ranges = dashboard_data["expected_ranges"]

    logger.info(f"Processing dashboard: {dashboard_name}")

    # 1. Rule-based checks
    rules = QualityRules()
    rule_issues = rules.check_all(metrics)

    # 2. Anomaly detection
    detector = AnomalyDetector()
    anomaly_issues = detector.detect(metrics)

    # 3. Validators
    validators = Validators()
    validation_issues = validators.validate(metrics, expected_ranges)

    all_issues = rule_issues + anomaly_issues + validation_issues

    # 4. AI insights
    ai = AIAnalyzer()
    entry = {"dashboard": dashboard_name, "issues": all_issues}
    entry = ai.analyze_all([entry])[0]

    # 5. Score
    scorer = ScoreCalculator()
    entry["score"] = scorer.calculate_score(entry["issues"])

    return entry


def main():
    logger.info("🚀 Starting AIDataQualityGuardian with MOCK DATA")

    # -----------------------------------------------
    # 1. Process dashboards
    # -----------------------------------------------
    results = []
    for d in MOCK_DASHBOARDS:
        results.append(process_dashboard(d))

    logger.info("All dashboards processed.")
    logger.info(Helper.to_pretty_json(results))

    # -----------------------------------------------
    # 2. Slack Report
    # -----------------------------------------------
    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_url:
        slack = SlackNotifier(slack_url)
        report_blocks = MessageTemplates.build_block_report(results)
        slack.send_blocks(report_blocks)
    else:
        logger.warning("Slack webhook not configured — skipping Slack alert.")

    # -----------------------------------------------
    # 3. Email Report
    # -----------------------------------------------
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
            logger.error("Error sending email: " + str(e))
    else:
        logger.warning("Email SMTP not configured — skipping email alert.")

    # -----------------------------------------------
    # 4. JIRA Integration
    # -----------------------------------------------
    jira = JiraExporter()
    for d in results:
        issue_url = jira.create_issue(d["dashboard"], d["issues"])
        if issue_url:
            logger.info(f"JIRA Ticket created: {issue_url}")

            # Also send to Slack
            if slack_url:
                slack.send_text(f"🐞 JIRA Ticket created: {issue_url}")

    # -----------------------------------------------
    # 5. Test generation
    # -----------------------------------------------
    test_builder = TestBuilder()
    tests = test_builder.build_tests(results)

    exporter = FileExporter("generated_tests")
    exporter.export_tests(tests)

    logger.info("Test generation completed.")
    logger.info("🎉 AIDataQualityGuardian run complete.")


if __name__ == "__main__":
    main()