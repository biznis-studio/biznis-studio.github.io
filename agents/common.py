"""Shared HTTP + logging helpers for all agents.

Every agent in this system only calls public, documented, no-auth-required
APIs (Hacker News/Algolia, Wikimedia, npm registry, Stack Exchange, GitHub
REST) strictly within their published rate limits and terms of use. No
scraping of pages that forbid it, no bypassing of auth walls, no synthetic
traffic.
"""
import time
import warnings
from datetime import datetime, timezone
from typing import Any, Optional

warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

import requests

USER_AGENT = "biznis-market-research-agent/0.1 (contact: jozefrusnak4@gmail.com)"
DEFAULT_TIMEOUT = 15
DEFAULT_HEADERS = {"User-Agent": USER_AGENT, "Accept": "application/json"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_get(url: str, params: Optional[dict] = None, retries: int = 2,
             backoff: float = 1.5, headers: Optional[dict] = None) -> Optional[Any]:
    """GET a URL and return parsed JSON, or None on failure (never raises)."""
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=DEFAULT_TIMEOUT)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 403) or resp.status_code >= 500:
                time.sleep(backoff * (attempt + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(backoff * (attempt + 1))
    return None
