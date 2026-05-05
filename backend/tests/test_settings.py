import pytest
from pydantic import ValidationError

from growth_op_agent.settings import load_settings


def test_load_settings_validates_expected_shape(tmp_path):
    path = tmp_path / "settings.yaml"
    path.write_text(
        """
intelligence:
  model: claude-opus-4-6
publishing:
  posts_per_day: 10
  schedule_times:
    - "09:00"
  timezone: UTC
analytics:
  performance_review_interval_hours: 24
"""
    )

    settings = load_settings(path)

    assert settings.intelligence.model == "claude-opus-4-6"
    assert settings.publishing.posts_per_day == 10
    assert settings.publishing.schedule_times == ["09:00"]
    assert settings.analytics.performance_review_interval_hours == 24


def test_load_settings_rejects_invalid_schedule_time(tmp_path):
    path = tmp_path / "settings.yaml"
    path.write_text(
        """
intelligence:
  model: claude-opus-4-6
publishing:
  posts_per_day: 10
  schedule_times:
    - "25:00"
  timezone: UTC
analytics:
  performance_review_interval_hours: 24
"""
    )

    with pytest.raises(ValidationError, match="Invalid schedule time"):
        load_settings(path)


def test_load_settings_rejects_invalid_timezone(tmp_path):
    path = tmp_path / "settings.yaml"
    path.write_text(
        """
intelligence:
  model: claude-opus-4-6
publishing:
  posts_per_day: 10
  schedule_times:
    - "09:00"
  timezone: Not/AZone
analytics:
  performance_review_interval_hours: 24
"""
    )

    with pytest.raises(ValidationError, match="Unknown timezone"):
        load_settings(path)
