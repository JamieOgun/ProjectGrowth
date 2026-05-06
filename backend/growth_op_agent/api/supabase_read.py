import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imljc2F0cWt6ZXVnc211aGR0dmR0Iiwicm9sZSI6Im"
    "Fub24iLCJpYXQiOjE3Nzc5ODQ1NjIsImV4cCI6MjA5MzU2MDU2Mn0"
    ".lzaq7oxOosTkWLOgcrYYfrfkjdsRG24M1Co6lE7ZsaI"
)


def select_daily_metrics(days: int) -> list[dict]:
    start_date = _start_date(days)
    return _select(
        "daily_metrics",
        {
            "select": "*",
            "date": f"gte.{start_date}",
            "order": "date.asc",
        },
    )


def select_audience_metrics(days: int) -> list[dict]:
    start_date = _start_date(days)
    return _select(
        "audience_metrics",
        {
            "select": "*",
            "date": f"gte.{start_date}",
            "order": "date.asc",
        },
    )


def select_latest_weekly_insights() -> dict | None:
    rows = _select(
        "weekly_insights",
        {
            "select": "*",
            "order": "generated_at.desc",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


def _select(table: str, params: dict[str, str]) -> list[dict]:
    query = urllib.parse.urlencode(params, safe=".,*")
    url = f"{_supabase_url()}/rest/v1/{table}?{query}"
    key = _read_key()
    req = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        raise RuntimeError(f"{table} select failed: HTTP {e.code} - {detail}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"{table} select failed: {e.reason}") from e


def _read_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or SUPABASE_ANON_KEY
    )


def _supabase_url() -> str:
    return os.getenv("SUPABASE_URL", "https://icsatqkzeugsmuhdtvdt.supabase.co")


def _start_date(days: int) -> str:
    return (date.today() - timedelta(days=days - 1)).isoformat()
