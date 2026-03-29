# AGENTS.md

Welcome to the YouTube MCP Server project! This document outlines the core conventions, setup instructions, and architecture principles for AI agents working in this repository.

> **Important**: This project enforces strict environmental management rules. You MUST read and follow `RULES.md` before executing any commands or installing dependencies.

## Project Overview

This project is a Model Context Protocol (MCP) server built with Python (`FastMCP`) that provides comprehensive YouTube data tools (videos, channels, playlists, transcripts). It uses an API key rotation mechanism to manage YouTube Data API quota limits.

## Setup

This project uses `uv` as the exclusive Python package manager.

```bash
# 1. Create a virtual environment (never install globally)
uv venv .venv

# 2. Activate the environment (REQUIRED)
source .venv/bin/activate

# 3. Install the application in editable mode with development dependencies
uv pip install -e ".[dev]"

# 4. Set up environment variables
cp .env.example .env
# Agent: Ensure prompt for user configuration if YOUTUBE_API_KEY is unset in .env
```

## Development

The application can be run locally or via Docker. The configuration is loaded from `.env` (secrets) and `config.yaml` (general settings).

**Locally (HTTP or stdio mode):**
```bash
# Make sure .venv is activated
source .venv/bin/activate

# Run in HTTP mode (default: http://localhost:8088/mcp)
python -m yt_mcp_server

# Run in stdio mode (for direct MCP client use)
python -m yt_mcp_server --transport stdio
```

**Using Docker Compose (Recommended for HTTP/SSE deployment):**
```bash
# Start the containers with build step
docker compose up -d --build

# View logs
docker compose logs -f yt-mcp-server
```

## Testing

The project uses `pytest` and `pytest-asyncio` for testing.

```bash
# Make sure .venv is activated
source .venv/bin/activate

# Run all tests
pytest

# Run tests with verbose output
pytest -v
```

## Code Style & Conventions

- **Layout**: The project strictly adheres to the `python-src-layout`. All core application code MUST reside inside `src/yt_mcp_server/`, while tests belong outside in the `tests/` directory.
- **Naming**: Follow `snake_case` for variables, functions, and internal services (`_a_function` for internal async, `_function` for internal sync). Class names should be `PascalCase`.
- **Dependencies**: Never use `pip install` directly. Always use `uv pip install`. Changes to dependencies MUST be reflected in `pyproject.toml`.
- **Type Hinting**: All code should have appropriate type hints (`from __future__ import annotations`).

## Project Structure

- `src/yt_mcp_server/__main__.py`: CLI entrypoint handling transport protocols.
- `src/yt_mcp_server/server.py`: The `FastMCP` instance where `@mcp.tool` endpoints are registered.
- `src/yt_mcp_server/_config.py`: Configuration singleton loading merging `.env` secrets and `config.yaml` values.
- `src/yt_mcp_server/services/`: Specific logic handlers (`video.py`, `channel.py`, `playlist.py`, `transcript.py`). Contains `YouTubeClientPool` that automatically rotates API keys on quota starvation (HTTP 403).
- `Dockerfile` & `docker-compose.yml`: Containerization setup using `nginx` as a reverse proxy for correct SSE header proxying.

## Security Notes

- **Secrets**: API Keys MUST ONLY be loaded from the `.env` file through `python-dotenv` environment variables. Do NOT hardcode API keys anywhere.
- **Committing**: Never commit the `.env` file to version control. The `.gitignore` is already configured to prevent this.

## OpenSpec Workflow (Experimental)

This codebase uses the `@openspec` workflow for architectural planning and task execution. 
- Use `/opsx-explore` to analyze ideas.
- Use `/opsx-propose` to plan new changes.
- Use `/opsx-apply` to implement approved tasks.
- Spec files are synced to `openspec/specs/` after change archival.