from src.utils.logger import logger


class QualityRules:
    """
    Basic Data Quality rules for KPI validation.
    """

    def check_all(self, metrics: dict) -> list:
        return self.check(metrics)

    def check(self, metrics: dict) -> list:
        issues = []

        for metric_name, values in metrics.items():

            # --- Clean numeric subset ---
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            # --- Rule 1: Null or zero values ---
            if any(v is None or v == 0 for v in values):
                issues.append({
                    "metric": metric_name,
                    "issue": "Null / Zero values",
                    "details": f"{metric_name} contains null/zero values: {values}"
                })

            # --- Rule 2: No variation ---
            if len(numeric_values) > 1 and len(set(numeric_values)) == 1:
                issues.append({
                    "metric": metric_name,
                    "issue": "No variation",
                    "details": f"{metric_name} has constant values: {values}"
                })

            # --- Rule 3: Negative values ---
            if any((v is not None and v < 0) for v in values):
                issues.append({
                    "metric": metric_name,
                    "issue": "Negative values",
                    "details": f"{metric_name} contains negative numbers: {values}"
                })

            # --- Rule 4: Extreme spikes (but skip None) ---
            if numeric_values:
                avg = sum(numeric_values) / len(numeric_values)
                if max(numeric_values) > avg * 5:
                    issues.append({
                        "metric": metric_name,
                        "issue": "Extremely large value detected",
                        "details": f"{metric_name} has extreme spikes: {values}"
                    })

        logger.info(f"Quality rules detected {len(issues)} issues.")
        return issues