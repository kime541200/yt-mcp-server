"""Configuration loader for yt_mcp_server.

Loads:
- Secrets from .env via python-dotenv
- Tunable parameters from config.yaml via pyyaml
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def _find_project_root() -> Path:
    """Walk upward from this file to find the project root (contains pyproject.toml)."""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return current


_PROJECT_ROOT = _find_project_root()

# Load .env once at import time — silently ignore if missing
load_dotenv(_PROJECT_ROOT / ".env")


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file, returning empty dict if missing."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass
class YouTubeConfig:
    default_max_results: int = 10
    default_transcript_language: str = "zh-TW"
    request_timeout_seconds: int = 30
    transcript_merge_max_gap_seconds: float = 1.5
    transcript_merge_target_chars: int = 180
    transcript_merge_max_duration_seconds: float = 30.0


@dataclass
class ServerConfig:
    name: str = "yt-mcp-server"
    version: str = "0.1.0"
    max_response_chars: int = 8000


@dataclass
class AppConfig:
    youtube: YouTubeConfig = field(default_factory=YouTubeConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    # API Keys — read from environment (loaded by dotenv above)
    @property
    def api_keys(self) -> list[str]:
        """Return all configured YouTube API keys, in order."""
        keys = [
            os.environ.get("YOUTUBE_API_KEY", ""),
            os.environ.get("YOUTUBE_API_KEY2", ""),
            os.environ.get("YOUTUBE_API_KEY3", ""),
        ]
        return [k.strip() for k in keys if k.strip()]

    @property
    def mcp_host(self) -> str:
        return os.environ.get("MCP_HOST", "127.0.0.1")

    @property
    def mcp_port(self) -> int:
        return int(os.environ.get("MCP_PORT", "8088"))

    @property
    def mcp_transport(self) -> str:
        return os.environ.get("MCP_TRANSPORT", "http").lower()


def load_config() -> AppConfig:
    """Load and return the merged AppConfig from config.yaml + .env."""
    raw = _load_yaml(_PROJECT_ROOT / "config.yaml")

    yt_raw = raw.get("youtube", {})
    srv_raw = raw.get("server", {})

    return AppConfig(
        youtube=YouTubeConfig(
            default_max_results=int(yt_raw.get("default_max_results", 10)),
            default_transcript_language=str(
                yt_raw.get("default_transcript_language", "zh-TW")
            ),
            request_timeout_seconds=int(yt_raw.get("request_timeout_seconds", 30)),
            transcript_merge_max_gap_seconds=float(
                yt_raw.get("transcript_merge_max_gap_seconds", 1.5)
            ),
            transcript_merge_target_chars=int(
                yt_raw.get("transcript_merge_target_chars", 180)
            ),
            transcript_merge_max_duration_seconds=float(
                yt_raw.get("transcript_merge_max_duration_seconds", 30.0)
            ),
        ),
        server=ServerConfig(
            name=str(srv_raw.get("name", "yt-mcp-server")),
            version=str(srv_raw.get("version", "0.1.0")),
            max_response_chars=int(srv_raw.get("max_response_chars", 8000)),
        ),
    )


# Singleton — import this everywhere
config: AppConfig = load_config()
