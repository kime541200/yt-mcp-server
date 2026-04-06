"""YouTube MCP Server — FastMCP server with all tool definitions.

Tools provided:
  Videos:      videos_getVideo, videos_searchVideos
  Channels:    channels_getChannel, channels_searchChannels, channels_listVideos
  Playlists:   playlists_getPlaylist, playlists_getPlaylistItems
  Transcripts: transcripts_getTranscript
"""

from __future__ import annotations

import json
import logging
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from yt_mcp_server._config import config
from yt_mcp_server.services.channel import ChannelService
from yt_mcp_server.services.playlist import PlaylistService
from yt_mcp_server.services.transcript import TranscriptService
from yt_mcp_server.services.video import VideoService

log = logging.getLogger(__name__)

# ── Singleton MCP server ─────────────────────────────────────────────────────
mcp = FastMCP(
    name=config.server.name,
    version=config.server.version,
)

# ── Service instances ────────────────────────────────────────────────────────
_video_svc = VideoService()
_channel_svc = ChannelService()
_playlist_svc = PlaylistService()
_transcript_svc = TranscriptService()


# ── Helper ───────────────────────────────────────────────────────────────────
def _serialize(obj: object) -> str:
    """JSON-serialize and truncate to max_response_chars."""
    raw = json.dumps(obj, ensure_ascii=False, indent=2)
    limit = config.server.max_response_chars
    if len(raw) > limit:
        raw = raw[:limit] + f"\n... [truncated {len(raw) - limit} chars]"
    return raw


# ── Videos ───────────────────────────────────────────────────────────────────
@mcp.tool(
    name="videos_getVideo",
    description="Get detailed information about a YouTube video (snippet, contentDetails, statistics).",
)
def videos_get_video(
    video_id: Annotated[str, Field(description="The YouTube video ID.")],
    parts: Annotated[
        list[str] | None,
        Field(description="Resource parts to return (default: snippet, contentDetails, statistics)."),
    ] = None,
) -> str:
    result = _video_svc.get_video(video_id, parts)
    if result is None:
        return f"No video found for ID: {video_id}"
    return _serialize(result)


@mcp.tool(
    name="videos_searchVideos",
    description="Search for YouTube videos by query with optional filters.",
)
def videos_search_videos(
    query: Annotated[str, Field(description="Search query string.")],
    max_results: Annotated[
        int | None,
        Field(description="Maximum number of results to return.", ge=1, le=50),
    ] = None,
    order: Annotated[
        str,
        Field(description="Sort order: relevance | date | rating | viewCount | title."),
    ] = "relevance",
    published_after: Annotated[
        str | None,
        Field(description="ISO 8601 datetime — only include videos published after this date."),
    ] = None,
    published_before: Annotated[
        str | None,
        Field(description="ISO 8601 datetime — only include videos published before this date."),
    ] = None,
    channel_id: Annotated[
        str | None,
        Field(description="Restrict results to a specific channel ID."),
    ] = None,
) -> str:
    results = _video_svc.search_videos(
        query=query,
        max_results=max_results,
        order=order,
        published_after=published_after,
        published_before=published_before,
        channel_id=channel_id,
    )
    return _serialize(results)


# ── Channels ─────────────────────────────────────────────────────────────────
@mcp.tool(
    name="channels_getChannel",
    description="Get information about a YouTube channel (snippet, statistics, brandingSettings).",
)
def channels_get_channel(
    channel_id: Annotated[str, Field(description="The YouTube channel ID.")],
    parts: Annotated[
        list[str] | None,
        Field(description="Resource parts to return."),
    ] = None,
) -> str:
    result = _channel_svc.get_channel(channel_id, parts)
    if result is None:
        return f"No channel found for ID: {channel_id}"
    return _serialize(result)


@mcp.tool(
    name="channels_searchChannels",
    description="Search for YouTube channels by name, handle, or keyword.",
)
def channels_search_channels(
    query: Annotated[str, Field(description="Channel search query or @handle.")],
    max_results: Annotated[
        int | None,
        Field(description="Maximum number of results to return.", ge=1, le=50),
    ] = None,
    order: Annotated[
        str,
        Field(description="Sort order: relevance | date | rating | viewCount | title."),
    ] = "relevance",
    channel_type: Annotated[
        str | None,
        Field(description="Channel type filter: any | show."),
    ] = None,
) -> str:
    results = _channel_svc.search_channels(
        query=query,
        max_results=max_results,
        order=order,
        channel_type=channel_type,
    )
    return _serialize(results)


@mcp.tool(
    name="channels_listVideos",
    description="List recent videos uploaded by a specific YouTube channel.",
)
def channels_list_videos(
    channel_id: Annotated[str, Field(description="The YouTube channel ID.")],
    max_results: Annotated[
        int | None,
        Field(description="Maximum number of videos to return.", ge=1, le=50),
    ] = None,
) -> str:
    results = _channel_svc.list_channel_videos(channel_id, max_results)
    return _serialize(results)


# ── Playlists ─────────────────────────────────────────────────────────────────
@mcp.tool(
    name="playlists_getPlaylist",
    description="Get metadata (title, description, item count) for a YouTube playlist.",
)
def playlists_get_playlist(
    playlist_id: Annotated[str, Field(description="The YouTube playlist ID.")],
    parts: Annotated[
        list[str] | None,
        Field(description="Resource parts to return."),
    ] = None,
) -> str:
    result = _playlist_svc.get_playlist(playlist_id, parts)
    if result is None:
        return f"No playlist found for ID: {playlist_id}"
    return _serialize(result)


@mcp.tool(
    name="playlists_getPlaylistItems",
    description="Get the videos contained in a YouTube playlist.",
)
def playlists_get_playlist_items(
    playlist_id: Annotated[str, Field(description="The YouTube playlist ID.")],
    max_results: Annotated[
        int | None,
        Field(description="Maximum number of items to return.", ge=1, le=50),
    ] = None,
) -> str:
    results = _playlist_svc.get_playlist_items(playlist_id, max_results)
    return _serialize(results)


# ── Transcripts ───────────────────────────────────────────────────────────────
@mcp.tool(
    name="transcripts_getTranscript",
    description=(
        "Get the transcript / subtitles for a YouTube video. "
        "Does NOT consume YouTube API quota."
    ),
)
def transcripts_get_transcript(
    video_id: Annotated[str, Field(description="The YouTube video ID.")],
    language: Annotated[
        str | None,
        Field(description="BCP-47 language code (e.g. 'zh-TW', 'en'). Defaults to config value."),
    ] = None,
) -> dict[str, object]:
    result = _transcript_svc.get_transcript(video_id, language)
    return result
