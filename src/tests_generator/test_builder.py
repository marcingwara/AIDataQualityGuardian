from src.utils.logger import logger


class TestBuilder:
    """
    Generates Python pytest-based test functions based on detected data quality issues.

    Input:
    [
        {
            "dashboard": "Sales Overview",
            "issues": [
                {
                    "metric": "Revenue",
                    "issue": "Sudden spike detected",
                    "details": "Value 5000 is > 3x above mean (1100.0)",
                    "ai_insight": "Possible duplicated mobile traffic rows."
                }
            ]
        }
    ]

    Output:
    Python code for tests, e.g.:

    def test_sales_overview_revenue_spike():
        assert last_value <= mean * 3
    """

    # ---------------------------
    # Build tests from issues
    # ---------------------------
    def build_tests(self, all_issues: list) -> dict:
        """
        Returns dict:
        {
            "Sales Overview": "def test_sales_overview_revenue_spike():\n    assert ...",
            ...
        }
        """

        tests_by_dashboard = {}

        for entry in all_issues:
            dashboard = entry.get("dashboard", "unknown_dashboard")
            issues = entry.get("issues", [])

            safe_dashboard_name = dashboard.lower().replace(" ", "_")
            test_code = []

            for issue in issues:
                metric = issue.get("metric", "metric")
                issue_type = issue.get("issue", "").lower()

                safe_metric = metric.lower().replace(" ", "_")

                test_name = f"test_{safe_dashboard_name}_{safe_metric}"

                # -------------- Test logic based on issue type ----------------

                if "spike" in issue_type:
                    code = (
                        f"def {test_name}_no_spike():\n"
                        f"    assert last_value <= mean * 3\n"
                    )

                elif "drop" in issue_type:
                    code = (
                        f"def {test_name}_no_drop():\n"
                        f"    assert last_value >= mean * 0.3\n"
                    )

                elif "null" in issue_type or "zero" in issue_type:
                    code = (
                        f"def {test_name}_no_nulls():\n"
                        f"    assert all(v not in [None, 0] for v in values)\n"
                    )

                elif "negative" in issue_type:
                    code = (
                        f"def {test_name}_no_negative_values():\n"
                        f"    assert all(v >= 0 for v in values)\n"
                    )

                elif "no variation" in issue_type:
                    code = (
                        f"def {test_name}_variation_exists():\n"
                        f"    assert len(set(values)) > 1\n"
                    )

                else:
                    code = (
                        f"def {test_name}_generic_quality_check():\n"
                        f"    assert False, 'Unexpected data quality issue detected.'\n"
                    )

                test_code.append(code)

            # join all generated tests
            tests_by_dashboard[dashboard] = "\n".join(test_code)

        logger.info("TestBuilder: generated test cases for all dashboards.")
        return tests_by_dashboard