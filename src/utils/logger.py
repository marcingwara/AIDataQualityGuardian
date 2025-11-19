import logging
import os


# -----------------------------
# Color formatting for terminal
# -----------------------------
class ColorFormatter(logging.Formatter):
    COLORS = {
        "INFO": "\033[94m",     # blue
        "WARNING": "\033[93m",  # yellow
        "ERROR": "\033[91m",    # red
        "DEBUG": "\033[90m",    # grey
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# -----------------------------
# Main logger configuration
# -----------------------------
logger = logging.getLogger("AIDataQualityGuardian")
logger.setLevel(logging.INFO)

# Formatter for console
console_formatter = ColorFormatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


# -----------------------------
# Optional File Logging
# -----------------------------
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"

if LOG_TO_FILE:
    file_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if not os.path.exists("logs"):
        os.makedirs("logs")

    file_handler = logging.FileHandler("logs/guardian.log")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)