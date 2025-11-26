import requests
from src.utils.logger import logger
import os


class JiraExporter:
    """
    Jira Spaces-compatible exporter.
    Uses ADF (Atlassian Document Format) for description (required on Jira Cloud).
    """

    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN")
        self.space_key = os.getenv("JIRA_SPACE_KEY")

        if not all([self.url, self.email, self.token, self.space_key]):
            logger.warning("JIRA exporter not fully configured — skipping JIRA integration.")
            self.enabled = False
            return

        self.enabled = True
        self.api_url = f"{self.url}/rest/api/3/issue"

        logger.info(f"[JIRA] Using space key: {self.space_key}")

    def _build_adf_description(self, dashboard_name, issues):
        """
        Jira Cloud requires ADF, not plain strings.
        """

        content = [
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Dashboard"}]
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": dashboard_name}]
            },
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Detected Issues"}]
            }
        ]

        # add each issue
        for item in issues:
            line = f"- {item['metric']}: {item['issue']} — {item['details']}"
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })

        return {
            "type": "doc",
            "version": 1,
            "content": content
        }

    def create_issue(self, dashboard_name, issues):
        if not self.enabled:
            logger.warning("JIRA disabled — skipping ticket creation.")
            return None

        summary = f"[Data Quality] Issues in {dashboard_name}"
        description_adf = self._build_adf_description(dashboard_name, issues)

        payload = {
            "fields": {
                "project": {"key": self.space_key},
                "summary": summary,
                "issuetype": {"name": "Task"},
                "description": description_adf
            }
        }

        logger.info(f"[JIRA] Creating issue in space '{self.space_key}'...")

        response = requests.post(
            self.api_url,
            json=payload,
            auth=(self.email, self.token),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in (200, 201):
            issue_key = response.json().get("key")
            url = f"{self.url}/browse/{issue_key}"
            logger.info(f"[JIRA] Successfully created → {url}")
            return url

        logger.error(f"[JIRA] Failed to create issue ({response.status_code}): {response.text}")
        return None