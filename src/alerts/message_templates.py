from datetime import datetime


class MessageTemplates:
    """
    Builds Slack Block Kit messages for Data Quality alerts.
    Used by SlackNotifier to send rich messages instead of plain text.
    """

    @staticmethod
    def build_block_report(all_issues: list):
        """
        Returns a Slack Block Kit JSON message.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not all_issues:
            return [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✔️ *All dashboards are healthy*\n_No issues detected as of {timestamp}_"
                    }
                }
            ]

        blocks = []

        # --- Title Block ---
        blocks.append({
            "type": "header",
            "text": {"type": "plain_text", "text": "🚨 Data Quality Alert"}
        })

        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"*Generated:* {timestamp}"}
            ]
        })

        blocks.append({"type": "divider"})

        # --- Dashboard-specific issues ---
        for entry in all_issues:
            dashboard_name = entry.get("dashboard", "Unknown Dashboard")
            issues = entry.get("issues", [])
            score = entry.get("score", 100)

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔴 Dashboard:* `{dashboard_name}`\n*Score:* {score}/100"
                }
            })

            for issue in issues:
                metric = issue.get("metric", "Unknown Metric")
                issue_name = issue.get("issue", "")
                details = issue.get("details", "")
                ai_insight = issue.get("ai_insight", "")

                issue_text = (
                    f"*• Metric:* `{metric}`\n"
                    f"  *Issue:* {issue_name}\n"
                    f"  *Details:* {details}"
                )

                if ai_insight:
                    issue_text += f"\n  *AI Insight:* _{ai_insight}_"

                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": issue_text}
                })

            blocks.append({"type": "divider"})

        return blocks