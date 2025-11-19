import json
from datetime import datetime
from src.utils.logger import logger


class Helper:
    """
    Generic helper functions used across the AIDataQualityGuardian project.
    """

    # ---------------------------
    # JSON pretty printing
    # ---------------------------
    @staticmethod
    def to_pretty_json(data):
        """Converts Python dict/list into formatted JSON string."""
        try:
            return json.dumps(data, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Helper.to_pretty_json error: {e}")
            return str(data)

    # ---------------------------
    # Save dict as JSON file
    # ---------------------------
    @staticmethod
    def save_json(file_path, data):
        """Saves dictionary or list to a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved JSON → {file_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON file {file_path}: {e}")

    # ---------------------------
    # Timestamp helpers
    # ---------------------------
    @staticmethod
    def now():
        """Returns current timestamp string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def now_for_filename():
        """Returns timestamp safe for filenames (no spaces/colons)."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    # ---------------------------
    # Safe extraction helpers
    # ---------------------------
    @staticmethod
    def safe_get(dct, path, default=None):
        """
        Extracts a nested field safely using a list of keys.

        Example:
        data = {"a": {"b": {"c": 10}}}
        Helper.safe_get(data, ["a", "b", "c"]) → 10
        """
        try:
            for key in path:
                dct = dct[key]
            return dct
        except Exception:
            return default

    # ---------------------------
    # List flattening
    # ---------------------------
    @staticmethod
    def flatten(nested_list):
        """
        Turns nested lists into a flat list.

        Example:
        [1, [2, 3], [4, [5]]] → [1, 2, 3, 4, 5]
        """
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.extend(Helper.flatten(item))
            else:
                result.append(item)
        return result

    # ---------------------------
    # Truncate long text
    # ---------------------------
    @staticmethod
    def truncate(text, limit=200):
        """
        Trims long text for UI/Slack messages.
        """
        if len(text) <= limit:
            return text
        return text[:limit] + "... (truncated)"