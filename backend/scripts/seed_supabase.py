"""Seed Supabase tables via REST API from existing JSON data files."""

import argparse
import hashlib
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from growth_op_agent.analytics.performance import build_daily_metrics

load_dotenv(Path(__file__).parent.parent / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://icsatqkzeugsmuhdtvdt.supabase.co")
WRITE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv(
    "SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imljc2F0cWt6ZXVnc211aGR0dmR0Iiwicm9sZSI6Im"
    "Fub24iLCJpYXQiOjE3Nzc5ODQ1NjIsImV4cCI6MjA5MzU2MDU2Mn0"
    ".lzaq7oxOosTkWLOgcrYYfrfkjdsRG24M1Co6lE7ZsaI",
)

DATA_DIR = Path(__file__).parent.parent / "data"
PERFORMANCE_DIR = DATA_DIR / "performance"


def _headers(merge: bool = False) -> dict:
    prefer = (
        "resolution=merge-duplicates,return=minimal"
        if merge
        else "resolution=ignore-duplicates,return=minimal"
    )
    return {
        "apikey": WRITE_KEY,
        "Authorization": f"Bearer {WRITE_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _post(table: str, rows: list[dict], on_conflict: str | None = None) -> None:
    if not rows:
        print(f"  {table}: no rows, skipping")
        return
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if on_conflict:
        url += f"?on_conflict={on_conflict}"
    body = json.dumps(rows).encode()
    req = urllib.request.Request(
        url, data=body, headers=_headers(merge=bool(on_conflict)), method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  {table}: {len(rows)} rows → {resp.status}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        print(f"  {table}: HTTP {e.code} — {detail}")
        raise


def _md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


# ── brand_config ─────────────────────────────────────────────────────────────


def seed_brand_config() -> None:
    from growth_op_agent.brand.brand_context import BrandContext

    path = Path(__file__).parent.parent / "config" / "brand_voice.yaml"
    brand = BrandContext.from_yaml(path)
    row = {
        "id": "main",
        "name": brand.name,
        "handle": brand.handle,
        "audience": brand.target_audience,
        "voice_brief": brand.voice_brief,
        "strategy_brief": brand.strategy_brief,
        "content_territories": brand.content_territories,
        "post_max_chars": brand.post_max_chars,
        "formats": [f.model_dump() for f in brand.formats],
    }
    _post("brand_config", [row], on_conflict="id")


# ── posts ────────────────────────────────────────────────────────────────────


def seed_posts() -> None:
    path = PERFORMANCE_DIR / "history.json"
    raw = json.loads(path.read_text())
    rows = []
    for p in raw:
        rows.append(
            {
                "id": p["id"],
                "text": p["text"],
                "published_at": p["published_at"],
                "post_type": p["post_type"],
                "likes": p.get("likes", 0),
                "retweets": p.get("retweets", 0),
                "replies": p.get("replies", 0),
                "impressions": p.get("impressions", 0),
                "conversation_id": p.get("conversation_id"),
                "referenced_tweets": p.get("referenced_tweets", []),
                "media": p.get("media", []),
            }
        )
    _post("posts", rows)


# ── ideas ────────────────────────────────────────────────────────────────────


def seed_ideas() -> None:
    ideas_dir = DATA_DIR / "ideas"
    for path in sorted(ideas_dir.glob("*.json")):
        generation_date = path.stem  # e.g. "2026-05-05"
        raw = json.loads(path.read_text())

        # File may be a list of IdeaRecord objects or raw PostIdea objects
        if isinstance(raw, list) and raw and "idea" in raw[0]:
            # IdeaRecord format: {id, idea: {content, rationale, format, estimated_engagement}, status, ...}
            rows = []
            for rec in raw:
                idea = rec["idea"]
                rows.append(
                    {
                        "id": rec["id"],
                        "generation_date": generation_date,
                        "content": idea["content"],
                        "rationale": idea["rationale"],
                        "format": idea["format"],
                        "estimated_engagement": idea["estimated_engagement"],
                        "status": rec.get("status", "generated"),
                        "created_at": rec.get("created_at"),
                        "updated_at": rec.get("updated_at"),
                    }
                )
        else:
            # Raw PostIdea list
            rows = []
            for idea in raw:
                rows.append(
                    {
                        "id": _md5(idea["content"]),
                        "generation_date": generation_date,
                        "content": idea["content"],
                        "rationale": idea["rationale"],
                        "format": idea["format"],
                        "estimated_engagement": idea["estimated_engagement"],
                        "status": "generated",
                        "created_at": f"{generation_date}T06:00:00+00:00",
                        "updated_at": f"{generation_date}T06:00:00+00:00",
                    }
                )
        _post("ideas", rows)


# ── daily_metrics ─────────────────────────────────────────────────────────────


def seed_daily_metrics() -> None:
    path = PERFORMANCE_DIR / "history.json"
    rows = [
        metric.model_dump(mode="json")
        for metric in build_daily_metrics(json.loads(path.read_text()))
    ]
    _post("daily_metrics", rows, on_conflict="date")


# ── weekly_insights ───────────────────────────────────────────────────────────


def seed_weekly_insights() -> None:
    insights_dir = PERFORMANCE_DIR / "insights"
    seen: set[tuple] = set()
    rows = []
    for path in sorted(insights_dir.glob("weekly_insights_*.json")):
        ins = json.loads(path.read_text())
        week_of = ins.get("week_of", {})
        year, week = week_of.get("year"), week_of.get("week")
        key = (year, week)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "year": year,
                "week": week,
                "generated_at": ins.get("generated_at"),
                "strategic_takeaways": ins.get("strategic_takeaways", []),
                "suggested_content_adjustments": ins.get(
                    "suggested_content_adjustments", []
                ),
            }
        )
    _post("weekly_insights", rows, on_conflict="year,week")


# ── audience_metrics ──────────────────────────────────────────────────────────


def seed_audience_metrics() -> None:
    path = PERFORMANCE_DIR / "follow_snapshots.json"
    raw = json.loads(path.read_text())
    rows = []
    for snap in raw if isinstance(raw, list) else raw.get("snapshots", []):
        recorded_at_raw = snap.get("captured_at") or snap.get("recorded_at")
        if not recorded_at_raw:
            continue
        date_str = datetime.fromisoformat(recorded_at_raw).date().isoformat()
        rows.append(
            {
                "date": date_str,
                "followers": snap.get("followers"),
                "following": snap.get("following"),
            }
        )
    _post("audience_metrics", rows, on_conflict="date")


SEEDERS = {
    "brand_config": seed_brand_config,
    "posts": seed_posts,
    "ideas": seed_ideas,
    "daily_metrics": seed_daily_metrics,
    "weekly_insights": seed_weekly_insights,
    "audience_metrics": seed_audience_metrics,
}


def main(targets: list[str] | None = None) -> None:
    selected = targets or list(SEEDERS)
    print("Seeding Supabase via REST API...")
    for target in selected:
        SEEDERS[target]()
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "targets",
        nargs="*",
        choices=SEEDERS,
        help="Tables to seed. Defaults to all tables.",
    )
    args = parser.parse_args()
    main(args.targets)
