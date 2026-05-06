from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

from growth_op_agent.api.helper import build_analytics_overview
from growth_op_agent.api.models import AnalyticsOverview
from growth_op_agent.api.supabase_read import (
    select_audience_metrics,
    select_daily_metrics,
    select_latest_weekly_insights,
)

load_dotenv()

app = FastAPI(title="GrowthOpAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
def analytics_overview(days: int = Query(default=7, ge=1, le=90)):
    daily = select_daily_metrics(days)
    audience = select_audience_metrics(days)
    insight = select_latest_weekly_insights()
    return build_analytics_overview(days, daily, audience, insight)
