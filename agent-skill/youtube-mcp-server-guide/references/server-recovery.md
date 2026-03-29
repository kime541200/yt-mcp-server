# Server Recovery Flow

Use this reference when the `yt-mcp-server` MCP server is not running, not reachable, or the MCP client cannot talk to it reliably.

## Recovery goal

Recover the environment without guessing. Follow this order:

1. Confirm the server is actually unavailable.
2. Recreate or refresh the local project if needed.
3. Ask the user for YouTube API keys.
4. Guide the user to the key setup instructions if they do not know how to get a key.

## 1) Verify the server

If `mcporter` is available, check server reachability before doing anything else:

- `mcporter list`
- `mcporter list <server_name> --schema`
- A lightweight `mcporter call` if the server appears in the list but still behaves oddly

If the server is missing or unreachable, stop retrying the same failing MCP call. Treat it as an environment problem first.

## 2) Clone or refresh the project

If the local project is missing, stale, or too broken to fix quickly, clone the repository from GitHub:

```bash
git clone https://github.com/kime541200/yt-mcp-server.git
```

After cloning, follow the repository README for setup and runtime instructions in the cloned directory.

## 3) Ask for YouTube API keys

This server needs at least one YouTube Data API key to work.

If the user already has a key, ask them to put it in the environment, usually in `.env`:

```env
YOUTUBE_API_KEY=...
```

If they have multiple keys, they can also provide `YOUTUBE_API_KEY2` and `YOUTUBE_API_KEY3` so the server can rotate quota automatically.

## 4) Guide users who do not know how to get a key

Tell them to open the key-creation guide inside the repository they just cloned:

- `<cloned-repo>/docs/how-to-get-yt-api-key.md`

Replace `<cloned-repo>` with the actual directory created by `git clone`. That guide explains how to create a Google Cloud project, enable YouTube Data API v3, and generate a restricted API key.

## Recommended recovery sequence

1. Verify the server is actually down.
2. Clone or refresh the repository if needed.
3. Ask the user for `YOUTUBE_API_KEY` or other configured keys.
4. If they do not know how to get a key, point them to the API key guide in the cloned repository.
5. Once the server is configured, re-run the `mcporter` preflight check.
