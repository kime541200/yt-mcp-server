# YouTube MCP Server

A modern, fast, and feature-rich Model Context Protocol (MCP) server for retrieving YouTube data, built with Python and `FastMCP`.

## Features

This server provides the following MCP tools to interact with YouTube:

- **Videos**: Get video details (`videos_getVideo`) and search videos (`videos_searchVideos`).
- **Channels**: Get channel details (`channels_getChannel`), search channels (`channels_searchChannels`), and list recent videos from a channel (`channels_listVideos`).
- **Playlists**: Get playlist metadata (`playlists_getPlaylist`) and list playlist items (`playlists_getPlaylistItems`).
- **Transcripts**: Get video transcripts (`transcripts_getTranscript`). *Note: This uses the `youtube-transcript-api` library and does **not** consume official YouTube API quota.*

## Prerequisites

To use this server, you need at least one YouTube Data API Key. 

👉 **For instructions on how to obtain a YouTube API key, please refer to: [How to get YouTube API Key](./docs/how-to-get-yt-api-key.md)**

## Setup & Configuration

### 1. Environment Variables

Copy the example environment file and add your YouTube API key:

```bash
cp .env.example .env
```

Edit the `.env` file to include your API key:
```env
YOUTUBE_API_KEY=your_actual_api_key_here
# Optional: Add multiple keys for automatic quota rotation
# YOUTUBE_API_KEY2=your_second_key
```

### 2. General Configuration

You can adjust non-sensitive parameters in `config.yaml` (e.g., default max results, transcript languages, timeout settings).

## Running the Server

You can run the server locally using Python or via Docker (recommended for background services).

### Option A: Running Locally (Python)

Ensure you have Python 3.13+ and `uv` installed.

```bash
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Run the server (default runs on HTTP transport at port 8088)
python -m yt_mcp_server

# Or run in standard I/O mode for direct MCP client integration
python -m yt_mcp_server --transport stdio
```

### Option B: Running with Docker (Recommended for HTTP/SSE)

The project includes a `docker-compose.yml` that wraps the API server behind an Nginx reverse proxy to properly handle Server-Sent Events (SSE).

```bash
# Build and start the containers in the background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop the containers
docker compose down
```

The server will be available at: `http://localhost:8088/mcp`

## Connecting an MCP Client

Depending on how you run the server, configure your MCP client as follows:

**For stdio mode (Local):**
```json
{
  "mcpServers": {
    "youtube": {
      "command": "python",
      "args": ["-m", "yt_mcp_server", "--transport", "stdio"],
      "env": {
        "YOUTUBE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**For HTTP/SSE mode (Docker/Local HTTP):**
Point your client to the FastMCP Streamable HTTP endpoint:
`http://localhost:8088/mcp`

## Using an Agent Skill for Better Results

This MCP server is designed to work well on its own, but you can get better results if the Agent you are using also has the companion skill:

- `agent-skill/youtube-mcp-server-guide/SKILL.md`

The MCP server and the Agent Skill are intentionally decoupled:

- The MCP server provides the YouTube tools.
- The Agent Skill teaches the Agent how to use those tools well, including when to choose search vs exact lookup, how to handle transcripts, and how to verify the server is actually reachable before use.

If your Agent supports custom skills, provide that skill alongside this MCP server so it can:

- check the server with `mcporter` before making tool calls
- choose the right YouTube tool faster
- handle common failure cases more gracefully

In practice, this means the same MCP server can be used by different Agents, and each Agent can become more effective simply by loading the skill that matches this server.
