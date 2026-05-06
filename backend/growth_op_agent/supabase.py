"""Small Supabase REST helper for best-effort runtime syncs."""

import json
import os
import urllib.error
import urllib.request

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://icsatqkzeugsmuhdtvdt.supabase.co")
SUPABASE_WRITE_KEY: str = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv(
        "SUPABASE_ANON_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imljc2F0cWt6ZXVnc211aGR0dmR0Iiwicm9sZSI6Im"
        "Fub24iLCJpYXQiOjE3Nzc5ODQ1NjIsImV4cCI6MjA5MzU2MDU2Mn0"
        ".lzaq7oxOosTkWLOgcrYYfrfkjdsRG24M1Co6lE7ZsaI",
    )
    or ""
)


def upsert_rows(table: str, rows: list[dict], on_conflict: str) -> None:
    if not rows:
        return

    url = f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}"
    headers = {
        "apikey": SUPABASE_WRITE_KEY,
        "Authorization": f"Bearer {SUPABASE_WRITE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    body = json.dumps(rows).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as e:
        print(f"{table} upsert failed: HTTP {e.code} - {e.read().decode()}")
    except urllib.error.URLError as e:
        print(f"{table} upsert failed: {e.reason}")
