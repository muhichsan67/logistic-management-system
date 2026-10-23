"""Rate limiter sliding-window in-memory (per proses).

Cukup untuk 1 instance. Jika deploy multi-worker/multi-instance, ganti storage ke Redis
dengan tetap mempertahankan signature dependency ini.
"""
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import Request

from app.core.config import get_settings
from app.core.exceptions import TooManyRequests

_hits: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(limit: int | None = None, window: int | None = None) -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        s = get_settings()
        max_hits, seconds = limit or s.AUTH_RATE_LIMIT, window or s.AUTH_RATE_WINDOW_SECONDS
        key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
        now = time.monotonic()
        q = _hits[key]
        while q and now - q[0] > seconds:
            q.popleft()
        if len(q) >= max_hits:
            raise TooManyRequests()
        q.append(now)

    return dependency
