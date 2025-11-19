from src.utils.logger import logger


class Validators:
    """
    Additional data validation utilities for AIDataQualityGuardian.
    """

    def validate(self, metrics: dict, expected_ranges: dict = None) -> list:
        issues = []

        for metric_name, values in metrics.items():

            # Rule 1 — Non-numeric values
            issues.extend(self._validate_numeric(metric_name, values))

            # Rule 2 — Out-of-range values (numeric only)
            if expected_ranges and metric_name in expected_ranges:
                issues.extend(self._validate_range(metric_name, values, expected_ranges[metric_name]))

            # Rule 3 — Minimum data length
            issues.extend(self._validate_min_length(metric_name, values))

        logger.info(f"Validators: detected {len(issues)} issues.")
        return issues

    # ---------------------------
    # Validate numeric
    # ---------------------------
    def _validate_numeric(self, metric_name, values):
        issues = []

        for v in values:
            if not isinstance(v, (int, float)):
                # Mark this as an issue
                issues.append({
                    "metric": metric_name,
                    "issue": "Non-numeric value",
                    "details": f"Value '{v}' is not a number."
                })

        return issues

    # ---------------------------
    # Validate expected ranges
    # ---------------------------
    def _validate_range(self, metric_name, values, expected_range):
        issues = []

        min_expected, max_expected = expected_range

        for v in values:

            # Skip None or invalid numeric types
            if not isinstance(v, (int, float)):
                issues.append({
                    "metric": metric_name,
                    "issue": "Out-of-range values",
                    "details": f"Invalid value '{v}' cannot be compared to expected range {min_expected}-{max_expected}"
                })
                continue

            # Check the range
            if not (min_expected <= v <= max_expected):
                issues.append({
                    "metric": metric_name,
                    "issue": "Out-of-range values",
                    "details": f"Value {v} outside expected range {min_expected}-{max_expected}"
                })

        return issues

    # ---------------------------
    # Validate minimum number of data points
    # ---------------------------
    def _validate_min_length(self, metric_name, values, min_len=3):
        if len(values) < min_len:
            return [{
                "metric": metric_name,
                "issue": "Insufficient data points",
                "details": f"{metric_name} has only {len(values)} values (min required: {min_len})"
            }]
        return []