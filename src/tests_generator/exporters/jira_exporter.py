import requests
from src.utils.logger import logger
import os

class JiraExporter:

    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.project_key = os.getenv("JIRA_PROJECT_KEY")

        if not all([self.url, self.email, self.token, self.project_key]):
            logger.warning("JIRA exporter not fully configured — skipping JIRA integration.")
            self.enabled = False
        else:
            self.enabled = True

        self.api_url = f"{self.url}/rest/api/3/issue"

    def create_issue(self, dashboard_name, issues):
        if not self.enabled:
            logger.warning("JIRA integration disabled — skipping issue creation.")
            return None

        summary = f"[AIDataQualityGuardian] Data Quality Issues in {dashboard_name}"
        description = "Detected data quality issues:\n\n"

        for item in issues:
            description += f"- *{item['metric']}*: {item['issue']} — {item['details']}\n"

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "issuetype": {"name": "Bug"},
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                                   {
                                       "type": "paragraph",
                                       "content": [
                                           {
                                               "type": "text",
                                               "text": "Detected data quality issues:"
                                           }
                                       ]
                                   }
                               ] + [
                                   {
                                       "type": "paragraph",
                                       "content": [
                                           {
                                               "type": "text",
                                               "text": f"- {item['metric']}: {item['issue']} — {item['details']}"
                                           }
                                       ]
                                   }
                                   for item in issues
                               ]
                }
            }
        }

        logger.info("Creating JIRA issue...")
        response = requests.post(
            self.api_url,
            json=payload,
            auth=(self.email, self.token),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in (200, 201):
            issue_key = response.json().get("key")
            issue_url = f"{self.url}/browse/{issue_key}"
            logger.info(f"JIRA issue created successfully → {issue_url}")
            return issue_url
        else:
            logger.error(f"Failed to create JIRA issue: {response.text}")
            return None