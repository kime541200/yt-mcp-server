"""Playlist service — wraps YouTube Data API calls for playlist resources."""

from __future__ import annotations

from typing import Any

from yt_mcp_server._config import config
from yt_mcp_server.services._youtube_client import youtube_pool


class PlaylistService:
    """Service for playlist-related YouTube API operations."""

    def get_playlist(
        self,
        playlist_id: str,
        parts: list[str] | None = None,
    ) -> dict[str, Any] | None:
        """Return metadata for a single playlist."""
        parts = parts or ["snippet", "contentDetails"]

        def _req(yt: Any) -> Any:
            return (
                yt.playlists()
                .list(part=",".join(parts), id=playlist_id)
                .execute()
            )

        response = youtube_pool.execute(_req)
        items = response.get("items", [])
        return items[0] if items else None

    def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return the videos contained in a playlist."""
        max_results = max_results or config.youtube.default_max_results

        def _req(yt: Any) -> Any:
            return (
                yt.playlistItems()
                .list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=max_results,
                )
                .execute()
            )

        response = youtube_pool.execute(_req)
        return response.get("items", [])
