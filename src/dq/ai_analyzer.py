import os
from src.utils.logger import logger
from src.config import Config

try:
    import openai
except ImportError:
    openai = None


class AIAnalyzer:
    """
    Optional AI module that interprets Data Quality issues
    and generates insights like:

    'Revenue spike may be caused by duplicated records or wrong joins.'

    Works in two modes:
    - AI mode (if OPENAI_API_KEY is provided)
    - fallback rule-based mode (no AI)
    """

    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY

        if self.api_key and openai:
            openai.api_key = self.api_key
            self.ai_enabled = True
            logger.info("AI Analyzer enabled (OpenAI API key detected).")
        else:
            self.ai_enabled = False
            logger.warning("AI Analyzer running in fallback mode (no OpenAI key).")

    # ---------------------------
    # AI mode (LLM)
    # ---------------------------
    def _ai_generate(self, issue):
        prompt = (
            "You are a data quality expert. Explain the possible cause for the following data issue:\n"
            f"Metric: {issue.get('metric')}\n"
            f"Issue: {issue.get('issue')}\n"
            f"Details: {issue.get('details')}\n"
            "Provide 1-2 clear, actionable sentences."
        )

        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=80,
                temperature=0.4
            )
            return response.choices[0].text.strip()

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return None

    # ---------------------------
    # Fallback mode (no AI)
    # ---------------------------
    def _fallback_generate(self, issue):
        metric = issue.get("metric", "")
        issue_type = issue.get("issue", "").lower()

        if "spike" in issue_type:
            return f"{metric} shows an unexpected spike — likely caused by duplicated rows or incorrect aggregation."

        if "drop" in issue_type:
            return f"{metric} dropped sharply — may indicate missing data or broken upstream pipeline."

        if "null" in issue_type or "zero" in issue_type:
            return f"{metric} contains null/zero values — check ETL validity or missing joins."

        if "no variation" in issue_type:
            return f"{metric} shows no variation — check if data refresh is working."

        if "negative" in issue_type:
            return f"{metric} contains negative values — likely a logical or transformation error."

        return "Potential data quality issue detected. Investigate upstream data sources."

    # ---------------------------
    # Public method
    # ---------------------------
    def analyze_issue(self, issue):
        """
        Returns text insight for a single issue.
        """
        if self.ai_enabled:
            insight = self._ai_generate(issue)
            if insight:
                return insight

        # fallback when no AI or error occurred
        return self._fallback_generate(issue)

    def analyze_all(self, all_issues):
        """
        Enhances report with AI insights for every detected issue.

        Input:
        [
            {
                "dashboard": "Sales Overview",
                "issues": [...]
            }
        ]

        Output: same structure but with added "ai_insight" field.
        """

        for entry in all_issues:
            for issue in entry.get("issues", []):
                issue["ai_insight"] = self.analyze_issue(issue)

        logger.info("AI insights added to all issues.")
        return all_issues