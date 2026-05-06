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


class Idea(BaseModel):
    id: str
    generation_date: str
    content: str
    rationale: str
    format: str
    estimated_engagement: str
    status: str
    created_at: str
    updated_at: str


class ContentFormat(BaseModel):
    name: str
    purpose: str
    max_chars: int | None = None
    template: str
    example: str | None = None


class BrandConfig(BaseModel):
    id: str
    name: str
    handle: str
    audience: str
    voice_brief: str
    strategy_brief: str
    content_territories: list[str]
    post_max_chars: int
    formats: list[ContentFormat]
    updated_at: str


class AnalyticsOverview(BaseModel):
    range: DateRange
    stat_cards: list[StatCard]
    follower_series: list[int]
    engagement_series: list[float]
    weekly_insight: WeeklyInsight | None = None
    posts: list[WeeklyPost]
