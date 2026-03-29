## 1. Project Setup & Package Management

- [x] 1.1 Create `src/yt_mcp_server` directory structure and `__init__.py` files specifically adhering to the python-src-layout convention.
- [x] 1.2 Update pyproject.toml to include the necessary python dependencies: `google-api-python-client`, `youtube-transcript-api`, `fastmcp`, `python-dotenv`, and `pyyaml`.
- [x] 1.3 Create a `.env.example` file and a `config.yaml` template in the root directory.

## 2. Core Utilities & Authentication

- [x] 2.1 Implement configuration loading logic utilizing `python-dotenv` for secrets alongside `yaml` for the `config.yaml`.
- [x] 2.2 Implement a `YouTubeClientPool` utility class that handles multiple `YOUTUBE_API_KEY` environmental variables using `google-api-python-client` builder.
- [x] 2.3 Add exception handlers to automatically rotate keys if a quota exhaustion error (HTTP 403) is encountered.

## 3. MCP Tools Definition

- [x] 3.1 Initialize the global FastMCP server instance inside `src/yt_mcp_server/main.py`.
- [x] 3.2 Implement the `@mcp.tool` function for `videos_getVideo` using the standard YouTube Data API.
- [x] 3.3 Implement the `@mcp.tool` function for `videos_searchVideos` to return matching contents using query parameters.
- [x] 3.4 Implement the `@mcp.tool` function for `channels_getChannel` to inspect specific YouTube channels.
- [x] 3.5 Implement the `@mcp.tool` function for `channels_searchChannels` to find channels by name.
- [x] 3.6 Implement the `@mcp.tool` function for `playlists_getPlaylist` and `playlists_getPlaylistItems` tools.
- [x] 3.7 Implement the `@mcp.tool` function for `transcripts_getTranscript` utilizing the `youtube-transcript-api` library to entirely sidestep the API quota limit.

## 4. Finalization & Execution Checks

- [x] 4.1 Write a `__main__.py` entrypoint inside the source module to handle running the FastMCP server standalone.
- [x] 4.2 Provide instructions or scripts for running the HTTP SSE server version locally.

