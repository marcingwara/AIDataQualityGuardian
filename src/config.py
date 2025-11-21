import os
from dotenv import load_dotenv

# ------------------------------------------
# FIX: always load .env from project root
# ------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# load .env explicitly
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    # Tableau Cloud
    TABLEAU_SERVER = os.getenv("TABLEAU_SERVER", "")
    TABLEAU_SITE = os.getenv("TABLEAU_SITE", "")
    TABLEAU_TOKEN_NAME = os.getenv("TABLEAU_TOKEN_NAME", "")
    TABLEAU_TOKEN_SECRET = os.getenv("TABLEAU_TOKEN_SECRET", "")

    # Slack
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")

    # Email
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = os.getenv("SMTP_PORT", "")
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "")
    EMAIL_TO = os.getenv("EMAIL_TO", "")

    # Jira
    JIRA_URL = os.getenv("JIRA_URL", "")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")