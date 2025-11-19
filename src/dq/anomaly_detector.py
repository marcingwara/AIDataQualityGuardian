import statistics
from src.utils.logger import logger


class AnomalyDetector:
    """
    Detects statistical anomalies in KPI data.
    """

    def detect(self, metrics: dict) -> list:
        issues = []

        for metric_name, values in metrics.items():

            # ------------------------------------------------
            # 1. Remove None or non-numeric values
            # ------------------------------------------------
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            if len(numeric_values) < 2:
                continue  # not enough numeric data for anomaly detection

            # ------------------------------------------------
            # 2. Safe numeric calculations
            # ------------------------------------------------
            mean = statistics.mean(numeric_values)
            stdev = statistics.pstdev(numeric_values) if len(numeric_values) > 1 else 0

            last_value = numeric_values[-1]

            # -----------------------------
            # Rule 1: Sudden spike
            # -----------------------------
            if last_value > mean * 3:
                issues.append({
                    "metric": metric_name,
                    "issue": "Sudden spike detected",
                    "details": f"Value {last_value} is > 3x above mean ({round(mean, 2)})"
                })

            # -----------------------------
            # Rule 2: Sudden drop
            # -----------------------------
            if last_value < mean * 0.3:
                issues.append({
                    "metric": metric_name,
                    "issue": "Sudden drop detected",
                    "details": f"Value {last_value} is < 30% of mean ({round(mean, 2)})"
                })

            # -----------------------------
            # Rule 3: Outlier detection
            # -----------------------------
            if stdev > 0 and abs(last_value - mean) > 2 * stdev:
                issues.append({
                    "metric": metric_name,
                    "issue": "Outlier detected",
                    "details": (
                        f"{last_value} differs from mean ({round(mean, 2)}) "
                        f"by > 2 standard deviations (σ={round(stdev, 2)})"
                    )
                })

        logger.info(f"Anomaly detector found {len(issues)} anomalies.")
        return issues