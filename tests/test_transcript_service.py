from __future__ import annotations

from dataclasses import dataclass

from youtube_transcript_api._errors import TranscriptsDisabled

from yt_mcp_server.services.transcript import TranscriptService


@dataclass
class _FakeSegment:
    text: str
    start: float
    duration: float


class _FakeTranscript:
    def __init__(
        self,
        *,
        language_code: str = "en",
        language: str = "English",
        is_generated: bool = False,
        is_translatable: bool = True,
        segments: list[_FakeSegment] | None = None,
    ) -> None:
        self.language_code = language_code
        self.language = language
        self.is_generated = is_generated
        self.is_translatable = is_translatable
        self._segments = segments or []

    def fetch(self) -> list[_FakeSegment]:
        return self._segments


class _FakeTranscriptList:
    def __init__(self, transcript: _FakeTranscript | None) -> None:
        self._transcript = transcript

    def find_transcript(self, languages: list[str]) -> _FakeTranscript:
        if self._transcript and self._transcript.language_code in languages:
            return self._transcript
        raise LookupError("not found")

    def __iter__(self):
        if self._transcript is None:
            return iter([])
        return iter([self._transcript])


def test_get_transcript_returns_structured_success(monkeypatch) -> None:
    fake_transcript = _FakeTranscript(
        language_code="en",
        language="English",
        is_generated=True,
        segments=[
            _FakeSegment(text="Hello world", start=3.2, duration=1.5),
            _FakeSegment(text="Second line", start=4.9, duration=2.0),
            _FakeSegment(text="Another block", start=3665.0, duration=2.0),
        ],
    )

    class _FakeApi:
        def list(self, video_id: str) -> _FakeTranscriptList:
            assert video_id == "abc123"
            return _FakeTranscriptList(fake_transcript)

    monkeypatch.setattr("yt_mcp_server.services.transcript.YouTubeTranscriptApi", lambda: _FakeApi())

    result = TranscriptService().get_transcript("abc123", language="zh-TW")

    assert result["status"] == "ok"
    assert result["requested_language"] == "zh-TW"
    assert result["language"] == "en"
    assert result["is_generated"] is True
    assert result["segment_count"] == 3
    assert result["merged_segment_count"] == 2
    assert result["full_text"] == "Hello world Second line Another block"
    assert result["merged_full_text"] == "Hello world Second line\n\nAnother block"
    assert result["transcript"][0]["timestamp"] == "00:03"
    assert result["transcript"][2]["timestamp"] == "01:01:05"
    assert result["merged_transcript"][0]["text"] == "Hello world Second line"
    assert result["merged_transcript"][0]["segment_count"] == 2
    assert result["merged_transcript"][1]["timestamp"] == "01:01:05"


def test_get_transcript_returns_structured_unavailable(monkeypatch) -> None:
    class _FakeApi:
        def list(self, video_id: str) -> _FakeTranscriptList:
            raise TranscriptsDisabled(video_id)

    monkeypatch.setattr("yt_mcp_server.services.transcript.YouTubeTranscriptApi", lambda: _FakeApi())

    result = TranscriptService().get_transcript("abc123", language="zh-TW")

    assert result["status"] == "unavailable"
    assert result["reason"] == "transcripts_disabled"
    assert result["language"] is None
    assert result["segment_count"] == 0
    assert result["merged_segment_count"] == 0
    assert result["transcript"] == []
    assert result["merged_transcript"] == []
