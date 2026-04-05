"""Transcript service — fetches YouTube video transcripts without consuming API quota.

Uses the third-party `youtube-transcript-api` library, which scrapes
YouTube's public transcript endpoint directly.
"""

from __future__ import annotations

from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from yt_mcp_server._config import config


class TranscriptService:
    """Service for fetching YouTube video transcripts."""

    def get_transcript(
        self,
        video_id: str,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Fetch the transcript for a video.

        Returns a dict with keys:
            video_id, language, transcript (list of {text, start, duration})
        """
        lang = language or config.youtube.default_transcript_language
        api = YouTubeTranscriptApi()

        try:
            transcript = api.fetch(
                video_id, languages=[lang, "en"]
            )
        except NoTranscriptFound:
            # Fall back to any available transcript
            try:
                transcript_list = api.list(video_id)
                transcript = next(iter(transcript_list)).fetch()
            except Exception as exc:
                raise RuntimeError(
                    f"No transcript available for video '{video_id}': {exc}"
                ) from exc
        except TranscriptsDisabled as exc:
            raise RuntimeError(
                f"Transcripts are disabled for video '{video_id}'."
            ) from exc

        return {
            "video_id": video_id,
            "language": lang,
            "transcript": [
                {
                    "text": getattr(seg, "text", "") if hasattr(seg, "text") else seg.get("text", ""),
                    "start": getattr(seg, "start", 0.0) if hasattr(seg, "start") else seg.get("start", 0.0),
                    "duration": getattr(seg, "duration", 0.0) if hasattr(seg, "duration") else seg.get("duration", 0.0),
                    "timestamp": _format_timestamp(getattr(seg, "start", 0.0) if hasattr(seg, "start") else seg.get("start", 0.0)),
                }
                for seg in transcript
            ],
        }


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS string."""
    total = int(seconds)
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"
