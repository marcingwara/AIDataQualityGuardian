import requests
from src.utils.logger import logger


class SlackNotifier:
    """
    Sends Slack notifications using:
    - simple text mode
    - Block Kit mode (recommended)

    Usage:
        notifier = SlackNotifier(webhook_url)
        notifier.send_text("Hello world")
        notifier.send_blocks(blocks_json)
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    # ---------------------------
    # Send plain text messages
    # ---------------------------
    def send_text(self, message: str) -> bool:
        if not self.webhook_url:
            logger.error("Slack webhook URL missing!")
            return False

        payload = {
            "text": message,
            "mrkdwn": True
        }

        try:
            response = requests.post(self.webhook_url, json=payload)

            if response.status_code != 200:
                logger.error(f"Slack text message failed: {response.text}")
                return False

            logger.info("Slack text message sent successfully.")
            return True

        except Exception as e:
            logger.error(f"Slack text send failed: {e}")
            return False

    # ---------------------------
    # Send Block Kit messages
    # ---------------------------
    def send_blocks(self, blocks: list) -> bool:
        if not self.webhook_url:
            logger.error("Slack webhook URL missing!")
            return False

        payload = {
            "blocks": blocks,
            "mrkdwn": True
        }

        try:
            response = requests.post(self.webhook_url, json=payload)

            if response.status_code != 200:
                logger.error(f"Slack Block Kit failed: {response.text}")
                return False

            logger.info("Slack Block Kit message sent successfully.")
            return True

        except Exception as e:
            logger.error(f"Slack Block Kit send failed: {e}")
            return False

    # ---------------------------
    # Automatic mode - chooses best format
    # ---------------------------
    def send_report(self, content):
        """
        Intelligent wrapper.
        If 'content' is a string → send_text
        If 'content' is a list (blocks) → send_blocks
        """

        if isinstance(content, str):
            return self.send_text(content)

        if isinstance(content, list):
            return self.send_blocks(content)

        logger.error("SlackNotifier.send_report: unknown content type")
        return False