import os
import httpx

ZENROWS_BASE = "https://api.zenrows.com/v1/"


async def zenrows_get(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
) -> httpx.Response:
    p = {
        "apikey": os.getenv("ZENROWS_API_KEY", ""),
        "url": url,
        **(params or {}),
    }
    return await client.get(ZENROWS_BASE, params=p, timeout=30)
