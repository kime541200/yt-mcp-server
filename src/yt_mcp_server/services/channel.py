"""Channel service — wraps YouTube Data API calls for channel resources."""

from __future__ import annotations

from typing import Any

from yt_mcp_server._config import config
from yt_mcp_server.services._youtube_client import youtube_pool


class ChannelService:
    """Service for channel-related YouTube API operations."""

    def get_channel(
        self,
        channel_id: str,
        parts: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Return detailed information for a single channel."""
        parts = parts or ["snippet", "statistics", "brandingSettings"]

        def _req(yt: Any) -> Any:
            return (
                yt.channels()
                .list(part=",".join(parts), id=channel_id)
                .execute()
            )

        response = youtube_pool.execute(_req)
        items = response.get("items", [])
        return items[0] if items else None

    def search_channels(
        self,
        query: str,
        max_results: int | None = None,
        order: str = "relevance",
        channel_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search YouTube channels by query."""
        max_results = max_results or config.youtube.default_max_results

        params: dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "maxResults": max_results,
            "order": order,
            "type": "channel",
        }
        if channel_type:
            params["channelType"] = channel_type

        def _req(yt: Any) -> Any:
            return yt.search().list(**params).execute()

        response = youtube_pool.execute(_req)
        return response.get("items", [])

    def list_channel_videos(
        self,
        channel_id: str,
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent videos uploaded by a channel."""
        max_results = max_results or config.youtube.default_max_results

        def _req(yt: Any) -> Any:
            return (
                yt.search()
                .list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=max_results,
                    order="date",
                    type="video",
                )
                .execute()
            )

        response = youtube_pool.execute(_req)
        return response.get("items", [])
