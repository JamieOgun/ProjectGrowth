"""Validated application settings loaded from config/settings.yaml."""

from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from pydantic import BaseModel, Field, field_validator


class IntelligenceSettings(BaseModel):
    model: str = Field(min_length=1)


class PublishingSettings(BaseModel):
    posts_per_day: int = Field(gt=0, le=100)
    schedule_times: list[str] = Field(default_factory=list)
    timezone: str = Field(min_length=1)

    @field_validator("schedule_times")
    @classmethod
    def validate_schedule_times(cls, values: list[str]) -> list[str]:
        for value in values:
            hour_text, separator, minute_text = value.partition(":")
            if separator != ":":
                raise ValueError(f"Invalid schedule time {value!r}; expected HH:MM.")
            if not hour_text.isdigit() or not minute_text.isdigit():
                raise ValueError(f"Invalid schedule time {value!r}; expected HH:MM.")
            hour = int(hour_text)
            minute = int(minute_text)
            if hour > 23 or minute > 59:
                raise ValueError(f"Invalid schedule time {value!r}; expected HH:MM.")
        return values

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as e:
            raise ValueError(f"Unknown timezone {value!r}.") from e
        return value


class AnalyticsSettings(BaseModel):
    performance_review_interval_hours: int = Field(gt=0)


class Settings(BaseModel):
    intelligence: IntelligenceSettings
    publishing: PublishingSettings
    analytics: AnalyticsSettings


def load_settings(path: Path) -> Settings:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Settings file {path} must contain a YAML object.")
    return Settings.model_validate(data)
