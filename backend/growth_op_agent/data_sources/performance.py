"""Reads pre-computed performance files — fully deterministic, no inline computation."""
from growth_op_agent.analytics.weekly_review import WeeklyInsights, latest_insights_path


class OwnPerformanceSource:
    def fetch_context(self) -> dict:
        """
        Returns weekly LLM strategic insights as a plain dict for injection into
        the daily idea-generation prompt.
        """
        path = latest_insights_path()
        if not path:
            return {}

        insights = WeeklyInsights.model_validate_json(path.read_text())
        return insights.model_dump(mode="json", exclude={"week_of", "generated_at"})
