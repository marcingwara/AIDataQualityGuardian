from src.utils.logger import logger


class ScoreCalculator:
    """
    Calculates Data Quality Score (0–100) for each dashboard.

    Score logic (simple & effective):
    - Start from 100
    - Subtract points per issue:
        - Critical anomalies: -25
        - Major quality issues: -15
        - Minor warnings: -5
    - Score cannot go below 0
    """

    def calculate_score(self, issues: list) -> int:
        score = 100

        for issue in issues:
            issue_name = issue.get("issue", "").lower()

            # Critical problems
            if "spike" in issue_name or "drop" in issue_name or "outlier" in issue_name:
                score -= 25

            # Major quality issues
            elif "null" in issue_name or "zero" in issue_name or "negative" in issue_name:
                score -= 15

            # Minor structural issues
            elif "no variation" in issue_name:
                score -= 5

        final_score = max(0, score)
        return final_score

    def add_scores(self, all_issues: list):
        """
        Enhances the full issue structure with a Data Quality Score.

        Input:
        [
            {
                "dashboard": "Sales Overview",
                "issues": [...],
                "score": 72
            }
        ]
        """

        for entry in all_issues:
            issues = entry.get("issues", [])
            score = self.calculate_score(issues)
            entry["score"] = score

        logger.info("Data Quality Scores computed for all dashboards.")
        return all_issues