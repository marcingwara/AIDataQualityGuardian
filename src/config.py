import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    TABLEAU_SITE = os.getenv("TABLEAU_SITE", "")
    TABLEAU_SERVER = os.getenv("TABLEAU_SERVER", "")
    TABLEAU_TOKEN_NAME = os.getenv("TABLEAU_TOKEN_NAME","")
    TABLEAU_TOKEN_SECRET = os.getenv("TABLEAU_TOKEN_SECRET","")

    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")

    DEBUG = os.getenv("DEBUG", "False").lower()== "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")