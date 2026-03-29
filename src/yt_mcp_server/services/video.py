"""Video service — wraps YouTube Data API calls for video resources."""

from __future__ import annotations

from typing import Any

from yt_mcp_server._config import config
from yt_mcp_server.services._youtube_client import youtube_pool


class VideoService:
    """Service for video-related YouTube API operations."""

    def get_video(
        self,
        video_id: str,
        parts: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Return detailed information for a single video."""
        parts = parts or ["snippet", "contentDetails", "statistics"]

        def _req(yt: Any) -> Any:
            return (
                yt.videos()
                .list(part=",".join(parts), id=video_id)
                .execute()
            )

        response = youtube_pool.execute(_req)
        items = response.get("items", [])
        return items[0] if items else None

    def search_videos(
        self,
        query: str,
        max_results: int | None = None,
        order: str = "relevance",
        published_after: str | None = None,
        published_before: str | None = None,
        channel_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search YouTube videos with optional filters."""
        max_results = max_results or config.youtube.default_max_results

        params: dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "maxResults": max_results,
            "order": order,
            "type": "video",
        }
        if published_after:
            params["publishedAfter"] = published_after
        if published_before:
            params["publishedBefore"] = published_before
        if channel_id:
            params["channelId"] = channel_id

        def _req(yt: Any) -> Any:
            return yt.search().list(**params).execute()

        response = youtube_pool.execute(_req)
        return response.get("items", [])
