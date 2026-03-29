"""YouTube API client pool with automatic key rotation on quota exhaustion.

Pattern:
- Initialize once from environment (via _config)
- On quota-related errors (HTTP 403), mark the current key exhausted and retry with the next
- If all keys are exhausted, raise a clear error
"""

from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from yt_mcp_server._config import config

log = logging.getLogger(__name__)

_QUOTA_ERROR_REASONS = frozenset(
    [
        "quotaExceeded",
        "dailyLimitExceeded",
        "userRateLimitExceeded",
        "rateLimitExceeded",
    ]
)

T = TypeVar("T")


def _is_quota_error(error: HttpError) -> bool:
    """Return True if the HttpError represents a quota / rate-limit issue."""
    # HTTP 403 is the canonical status for quota errors
    if error.status_code != 403:
        return False

    # Check error details if available
    error_details = error.error_details or []
    for detail in error_details:
        if detail.get("reason") in _QUOTA_ERROR_REASONS:
            return True

    # Fallback: check the reason field in the body
    try:
        body = error.error_details  # already parsed
    except Exception:
        body = []

    message = str(error).lower()
    return any(kw in message for kw in ("quota", "daily limit", "rate limit"))


class YouTubeClientPool:
    """Pool of YouTube Data API v3 clients, one per configured API key.

    Usage::

        result = await pool.execute(lambda yt: yt.videos().list(...).execute())
    """

    def __init__(self) -> None:
        self._clients: list[Any] = []
        self._exhausted: set[int] = set()
        self._initialized = False

    def _initialize(self) -> None:
        if self._initialized:
            return

        keys = config.api_keys
        if not keys:
            raise RuntimeError(
                "No YouTube API key configured. "
                "Set YOUTUBE_API_KEY (and optionally YOUTUBE_API_KEY2/3) in your .env file."
            )

        self._clients = [
            build("youtube", "v3", developerKey=key, cache_discovery=False)
            for key in keys
        ]
        self._initialized = True
        log.info("YouTubeClientPool initialized with %d key(s).", len(self._clients))

    @property
    def _available_indexes(self) -> list[int]:
        available = [i for i in range(len(self._clients)) if i not in self._exhausted]
        # If all keys are exhausted, attempt all of them (let the error propagate)
        return available if available else list(range(len(self._clients)))

    def execute(self, request_fn: Callable[[Any], T]) -> T:
        """Execute *request_fn(youtube_client)* with automatic key rotation."""
        self._initialize()

        last_error: Exception | None = None

        for idx in self._available_indexes:
            try:
                return request_fn(self._clients[idx])
            except HttpError as exc:
                if _is_quota_error(exc):
                    self._exhausted.add(idx)
                    log.warning(
                        "YouTube API key #%d quota exhausted — trying next key.", idx + 1
                    )
                    last_error = exc
                    continue
                raise  # non-quota errors bubble up immediately

        raise RuntimeError(
            "All configured YouTube API keys are exhausted."
            + (f" Last error: {last_error}" if last_error else "")
        )


# Module-level singleton — import this everywhere
youtube_pool = YouTubeClientPool()
