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
            status, reason, language, full_text, transcript, merged_transcript
        """
        requested_language = language or config.youtube.default_transcript_language
        api = YouTubeTranscriptApi()

        try:
            transcript_list = api.list(video_id)
        except TranscriptsDisabled as exc:
            return _build_unavailable_response(
                video_id=video_id,
                requested_language=requested_language,
                reason="transcripts_disabled",
                message=f"Transcripts are disabled for video '{video_id}'.",
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to list transcripts for video '{video_id}': {exc}"
            ) from exc

        transcript_source = _select_transcript(
            transcript_list=transcript_list,
            requested_language=requested_language,
        )
        if transcript_source is None:
            return _build_unavailable_response(
                video_id=video_id,
                requested_language=requested_language,
                reason="no_transcript_found",
                message=f"No transcript available for video '{video_id}'.",
            )

        try:
            transcript = transcript_source.fetch()
        except NoTranscriptFound:
            return _build_unavailable_response(
                video_id=video_id,
                requested_language=requested_language,
                reason="no_transcript_found",
                message=f"No transcript available for video '{video_id}'.",
            )
        except TranscriptsDisabled:
            return _build_unavailable_response(
                video_id=video_id,
                requested_language=requested_language,
                reason="transcripts_disabled",
                message=f"Transcripts are disabled for video '{video_id}'.",
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch transcript for video '{video_id}': {exc}"
            ) from exc

        segments = [
            {
                "text": str(_get_segment_value(seg, "text", "")).strip(),
                "start": float(_get_segment_value(seg, "start", 0.0)),
                "duration": float(_get_segment_value(seg, "duration", 0.0)),
                "timestamp": _format_timestamp(float(_get_segment_value(seg, "start", 0.0))),
            }
            for seg in transcript
        ]
        segments = [segment for segment in segments if str(segment["text"]).strip()]
        merged_segments = _merge_transcript_segments(segments)

        return {
            "video_id": video_id,
            "status": "ok",
            "reason": None,
            "requested_language": requested_language,
            "language": _get_transcript_attr(transcript_source, "language_code"),
            "language_label": _get_transcript_attr(transcript_source, "language"),
            "is_generated": bool(_get_transcript_attr(transcript_source, "is_generated", False)),
            "is_translatable": bool(_get_transcript_attr(transcript_source, "is_translatable", False)),
            "segment_count": len(segments),
            "merged_segment_count": len(merged_segments),
            "full_text": " ".join(segment["text"] for segment in segments).strip(),
            "merged_full_text": "\n\n".join(segment["text"] for segment in merged_segments).strip(),
            "transcript": segments,
            "merged_transcript": merged_segments,
        }


def _format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or HH:MM:SS string."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _select_transcript(transcript_list: Any, requested_language: str) -> Any | None:
    preferred_languages = [requested_language, "en"]

    for language_code in preferred_languages:
        if not language_code:
            continue
        try:
            return transcript_list.find_transcript([language_code])
        except Exception:
            continue

    try:
        return next(iter(transcript_list))
    except StopIteration:
        return None


def _build_unavailable_response(
    *,
    video_id: str,
    requested_language: str,
    reason: str,
    message: str,
) -> dict[str, Any]:
    return {
        "video_id": video_id,
        "status": "unavailable",
        "reason": reason,
        "message": message,
        "requested_language": requested_language,
        "language": None,
        "language_label": None,
        "is_generated": None,
        "is_translatable": None,
        "segment_count": 0,
        "merged_segment_count": 0,
        "full_text": "",
        "merged_full_text": "",
        "transcript": [],
        "merged_transcript": [],
    }


def _get_segment_value(segment: Any, key: str, default: Any) -> Any:
    if hasattr(segment, key):
        return getattr(segment, key)
    if isinstance(segment, dict):
        return segment.get(key, default)
    return default


def _get_transcript_attr(transcript: Any, key: str, default: Any = None) -> Any:
    if hasattr(transcript, key):
        return getattr(transcript, key)
    if isinstance(transcript, dict):
        return transcript.get(key, default)
    return default


def _merge_transcript_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not segments:
        return []

    max_gap = config.youtube.transcript_merge_max_gap_seconds
    target_chars = config.youtube.transcript_merge_target_chars
    max_duration = config.youtube.transcript_merge_max_duration_seconds

    merged: list[dict[str, Any]] = []
    current_group: list[dict[str, Any]] = []

    for segment in segments:
        if not current_group:
            current_group.append(segment)
            continue

        previous = current_group[-1]
        current_text_length = sum(len(item["text"]) for item in current_group)
        current_start = float(current_group[0]["start"])
        previous_end = float(previous["start"]) + float(previous["duration"])
        next_end = float(segment["start"]) + float(segment["duration"])
        gap = float(segment["start"]) - previous_end
        projected_length = current_text_length + len(segment["text"])
        projected_duration = next_end - current_start

        should_split = False
        if gap > max_gap:
            should_split = True
        elif projected_length > target_chars and current_text_length >= max(target_chars // 2, 60):
            should_split = True
        elif projected_duration > max_duration and current_text_length >= 40:
            should_split = True

        if should_split:
            merged.append(_build_merged_segment(current_group))
            current_group = [segment]
        else:
            current_group.append(segment)

    if current_group:
        merged.append(_build_merged_segment(current_group))

    return merged


def _build_merged_segment(group: list[dict[str, Any]]) -> dict[str, Any]:
    start = float(group[0]["start"])
    end = float(group[-1]["start"]) + float(group[-1]["duration"])
    text = " ".join(str(item["text"]).strip() for item in group if str(item["text"]).strip()).strip()
    return {
        "text": text,
        "start": start,
        "end": end,
        "duration": end - start,
        "timestamp": _format_timestamp(start),
        "segment_count": len(group),
    }
