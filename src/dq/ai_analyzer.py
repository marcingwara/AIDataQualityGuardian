from src.utils.logger import logger
from src.config import Config
import time

try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


class AIAnalyzer:
    """
    ULTRA FAST AI ANALYZER (Batch Mode)
    -----------------------------------
    - zamiast 5–10 osobnych zapytań do OpenAI → jedno batch request
    - czas wykonania spada z 2 minut → ~6–8 sekund
    - kompatybilne z gpt-4o-mini i gpt-4o

    Fallback: jeśli AI niedostępne → klasyczne reguły tekstowe.
    """

    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY

        if self.api_key and OPENAI_AVAILABLE:
            # ✅ FIXED: Dodany timeout i http_client dla GitHub Actions
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    timeout=httpx.Timeout(60.0, connect=10.0),  # 60s total, 10s connect
                    max_retries=3,
                    http_client=httpx.Client(
                        limits=httpx.Limits(
                            max_keepalive_connections=5,
                            max_connections=10,
                            keepalive_expiry=30
                        )
                    )
                )
                self.ai_enabled = True
                logger.info("🤖 AI Analyzer enabled (OpenAI key detected). ULTRA MODE ACTIVE.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.ai_enabled = False
        else:
            self.ai_enabled = False
            logger.warning("AI Analyzer running in fallback mode (no OpenAI key).")

    # ----------------------------------------------------------------------
    # FALLBACK MODE — jeśli AI nie działa
    # ----------------------------------------------------------------------
    def _fallback(self, issue):
        metric = issue.get("metric", "")
        issue_type = issue.get("issue", "").lower()

        if "spike" in issue_type:
            return f"{metric} shows a spike — likely duplicated rows or incorrect aggregation."
        if "drop" in issue_type:
            return f"{metric} dropped sharply — pipeline failure or missing data."
        if "null" in issue_type or "zero" in issue_type:
            return f"{metric} contains null/zero values — ETL or join issue."
        if "no variation" in issue_type:
            return f"{metric} is flat — extract may be frozen."
        if "negative" in issue_type:
            return f"{metric} contains negative values — logic or transformation error."

        return "Potential data quality issue detected. Investigate upstream sources."

    # ----------------------------------------------------------------------
    # BATCH MODE — ULTRA FAST GPT INFERENCE (WITH RETRY)
    # ----------------------------------------------------------------------
    def _batch_generate(self, issues, max_retries=3):
        """
        Wysyła *jedno* zapytanie do OpenAI zamiast wielu.
        issues = list of issues dictionaries

        ✅ FIXED: Dodany retry mechanism z exponential backoff
        """

        instruction = (
            "You are a senior data quality engineer. "
            "For each issue, produce a short, clear, actionable explanation "
            "of the likely root cause. Keep each answer to 1–2 sentences.\n\n"
            "Return ONLY a JSON list of strings in the same order."
        )

        messages = [
            {
                "role": "system",
                "content": instruction
            },
            {
                "role": "user",
                "content": str(issues)
            }
        ]

        # ✅ FIXED: Retry loop z exponential backoff
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2,
                    max_tokens=400,
                    timeout=45  # ✅ Per-request timeout
                )

                raw = response.choices[0].message.content

                # próbujemy zdekodować czystą listę JSON
                import json
                suggestions = json.loads(raw)

                if not isinstance(suggestions, list):
                    raise ValueError("Model did not return list")

                logger.info(f"✅ AI batch call succeeded on attempt {attempt + 1}")
                return suggestions

            except Exception as e:
                wait_time = (attempt + 1) * 2  # 2s, 4s, 6s
                logger.warning(f"⚠️ AI batch call attempt {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ AI batch call failed after {max_retries} attempts. Using fallback.")
                    return None

        return None

    # ----------------------------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------------------------
    def analyze_all(self, dashboards):
        """
        dashboards:
        [
            {
                "dashboard": "Sales Overview",
                "issues": [ ... ]
            }
        ]

        Modyfikuje strukturę danych:
        issue["ai_insight"] = "...text..."
        """

        for entry in dashboards:
            issues = entry.get("issues", [])
            if not issues:
                continue

            # If AI disabled → fallback for all issues
            if not self.ai_enabled:
                for issue in issues:
                    issue["ai_insight"] = self._fallback(issue)
                continue

            # ----------- AI MODE (BATCH) --------------
            batch_input = [
                {
                    "metric": i.get("metric"),
                    "issue": i.get("issue"),
                    "details": i.get("details"),
                }
                for i in issues
            ]

            suggestions = self._batch_generate(batch_input)

            if suggestions is None:
                # fallback if model fails
                logger.warning("⚠️ Using fallback insights due to AI failure")
                for issue in issues:
                    issue["ai_insight"] = self._fallback(issue)
            else:
                # map suggestions 1:1
                for issue, insight in zip(issues, suggestions):
                    issue["ai_insight"] = insight

        logger.info("AI insights added to all issues.")
        return dashboards