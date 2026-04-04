"""Rate limit monitoring via httpx client event hooks."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

_WARN_THRESHOLD = 0.20  # warn when < 20% remaining


def _cache_path() -> Path:
    """Path to the rate limit cache file."""
    import os

    xdg_cache = os.environ.get("XDG_CACHE_HOME", "")
    cache_dir = Path(xdg_cache) / "td" if xdg_cache else Path.home() / ".cache" / "td"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "rate_limit.json"


class RateLimitMonitor:
    """Captures rate limit headers from API responses."""

    def __init__(self) -> None:
        self.remaining: int | None = None
        self.limit: int | None = None

    def hook(self, response: httpx.Response) -> None:
        """httpx response event hook — called after every API response."""
        raw_remaining = response.headers.get("X-Ratelimit-Remaining")
        raw_limit = response.headers.get("X-Ratelimit-Limit")

        if raw_remaining is not None:
            self.remaining = int(raw_remaining)
        if raw_limit is not None:
            self.limit = int(raw_limit)

        # Debug logging
        if self.remaining is not None and self.limit is not None:
            logger.debug(
                "API %s (%d/%d remaining)", response.status_code, self.remaining, self.limit
            )

        # Warn on stderr if approaching limit
        if (
            self.remaining is not None
            and self.limit is not None
            and self.limit > 0
            and (self.remaining / self.limit) < _WARN_THRESHOLD
        ):
            print(
                f"Warning: {self.remaining}/{self.limit} API calls remaining",
                file=sys.stderr,
            )

        # Persist to cache
        self._save_cache()

    def _save_cache(self) -> None:
        """Persist current rate limit state to disk."""
        if self.remaining is None:
            return
        try:
            path = _cache_path()
            data = {"remaining": self.remaining, "limit": self.limit}
            from td.core.cache import atomic_write

            atomic_write(path, json.dumps(data))
        except Exception:
            pass


def load_rate_limit_cache() -> dict[str, int | None]:
    """Load cached rate limit data. Returns {remaining, limit}."""
    try:
        path = _cache_path()
        if path.exists():
            data = json.loads(path.read_text())
            return {
                "remaining": data.get("remaining"),
                "limit": data.get("limit"),
            }
    except Exception:
        pass
    return {"remaining": None, "limit": None}


# Singleton monitor — shared across the client
_monitor = RateLimitMonitor()


def get_monitor() -> RateLimitMonitor:
    """Get the global rate limit monitor."""
    return _monitor


def create_monitored_client() -> httpx.Client:
    """Create an httpx.Client with rate limit monitoring."""
    return httpx.Client(event_hooks={"response": [_monitor.hook]})
