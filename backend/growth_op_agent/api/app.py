from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from growth_op_agent.api.helper import build_analytics_overview
from growth_op_agent.api.models import AnalyticsOverview, BrandConfig, Idea
from growth_op_agent.api.supabase_read import (
    select_audience_metrics,
    select_brand_config,
    select_daily_metrics,
    select_ideas,
    select_latest_weekly_insights,
)
from growth_op_agent.brand import BrandContext
from growth_op_agent.content.idea_generator import IdeaGenerator
from growth_op_agent.content.idea_store import IdeaStore
from growth_op_agent.data_sources.aggregator import DataAggregator
from growth_op_agent.intelligence import IntelligenceLayer
from growth_op_agent.supabase import upsert_rows

IDEAS_DIR = Path("data/ideas")

load_dotenv()

app = FastAPI(title="GrowthOpAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/brand", response_model=BrandConfig)
def brand_config():
    row = select_brand_config()
    if row is None:
        raise HTTPException(status_code=404, detail="Brand config not found")
    return row


@app.post("/api/ideas/generate", response_model=list[Idea])
async def generate_ideas(n: int = Query(default=10, ge=1, le=20)):
    brand_row = select_brand_config()
    if brand_row is None:
        raise HTTPException(status_code=404, detail="Brand config not found")

    brand = BrandContext.from_supabase_row(brand_row)
    generator = IdeaGenerator(
        intelligence=IntelligenceLayer(brand),
        aggregator=DataAggregator(),
        brand=brand,
    )

    await generator.generate_daily(n=n)

    today = date.today().isoformat()
    records = IdeaStore(IDEAS_DIR / f"{today}.json").load()
    rows = [
        {
            "id": rec.id,
            "generation_date": today,
            "content": rec.idea.content,
            "rationale": rec.idea.rationale,
            "format": rec.idea.format,
            "estimated_engagement": rec.idea.estimated_engagement,
            "status": rec.status.value,
            "created_at": rec.created_at.isoformat(),
            "updated_at": rec.updated_at.isoformat(),
        }
        for rec in records
    ]
    upsert_rows("ideas", rows, on_conflict="id")
    return rows


@app.get("/api/ideas", response_model=list[Idea])
def ideas(
    status: str | None = Query(default=None, pattern="^(generated|rejected)$"),
    limit: int = Query(default=50, ge=1, le=200),
):
    return select_ideas(status=status, limit=limit)


@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
def analytics_overview(days: int = Query(default=7, ge=1, le=90)):
    daily = select_daily_metrics(days)
    audience = select_audience_metrics(days)
    insight = select_latest_weekly_insights()
    return build_analytics_overview(days, daily, audience, insight)
