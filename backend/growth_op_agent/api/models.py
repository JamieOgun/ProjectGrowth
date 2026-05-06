from pydantic import BaseModel, Field


class DateRange(BaseModel):
    days: int
    start_date: str
    end_date: str


class StatCard(BaseModel):
    label: str
    value: str
    delta: str
    positive: bool


class WeeklyPost(BaseModel):
    day: str
    format: str
    hook: str
    impressions: int
    eng: int
    replies: int
    rate: float


class WeeklyInsight(BaseModel):
    summary: str
    suggestions: list[str] = Field(default_factory=list)


class AnalyticsOverview(BaseModel):
    range: DateRange
    stat_cards: list[StatCard]
    follower_series: list[int]
    engagement_series: list[float]
    weekly_insight: WeeklyInsight | None = None
    posts: list[WeeklyPost]
