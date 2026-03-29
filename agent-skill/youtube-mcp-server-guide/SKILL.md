---
name: youtube-mcp-server-guide
description: Use this skill whenever you are connected to the yt-mcp-server MCP tools and the task involves YouTube videos, channels, playlists, transcripts, URLs, handles, recent uploads, YouTube API-backed retrieval, or verifying that the server is actually reachable with mcporter before use. It teaches which tool to call, how to extract IDs from YouTube URLs, when to use search vs exact lookup, and how to handle quota or transcript failures.
---

# YouTube MCP Server Usage

Use this skill as the operating manual for the `yt-mcp-server` MCP server.

The goal is simple: help the agent choose the right YouTube tool quickly, avoid ambiguous searches when an exact lookup is available, and handle the server's real-world constraints like quota rotation and response truncation.

If `mcporter` is available, use it as a quick preflight check before relying on the MCP server. That helps catch the common failure case where the skill is available but the actual server is not running or not reachable yet.

## What this server is for

Use the server to retrieve structured YouTube data:

- Video metadata and search results
- Channel metadata, channel search, and recent uploads
- Playlist metadata and playlist items
- Video transcripts and subtitles

Treat the MCP tools as the source of truth for YouTube-specific facts. If the user wants something the server can fetch, use the tools instead of guessing from memory.

## Preflight check with mcporter

Before using the YouTube MCP tools in a new session, verify the server is actually reachable.

If `mcporter` is installed, use it this way:

1. List configured servers with `mcporter list` and confirm the YouTube server appears.
2. Inspect the server schema with `mcporter list <server_name> --schema` when you need to confirm available tools.
3. Run a lightweight call if needed to verify the server responds before doing a larger task.

If `mcporter` is not installed, install it with `npm install -g mcporter` and then repeat the preflight check.

If the server is missing from the list or the call fails, treat that as an environment problem first. Tell the user the MCP server is not started or not reachable rather than pretending the tool call failed semantically.

## First decision

Classify the request before calling anything:

- If the user wants to find a video, channel, or playlist by topic, use search.
- If the user already has a video ID, channel ID, or playlist ID, use the exact lookup tool.
- If the user wants a channel's recent uploads, use the channel video listing tool.
- If the user wants subtitles, a quote, a timestamped excerpt, or a transcript summary, use the transcript tool.

When the user gives a YouTube URL, extract the identifier first:

- `watch?v=...` or `youtu.be/...` -> video ID
- `playlist?list=...` -> playlist ID
- channel URLs -> channel ID or `@handle` if available

If the URL is the only input and the identifier is not obvious, search for the resource rather than asking the user to reformat it unless the request is genuinely ambiguous.

## Tool selection

### Videos

Use `videos_getVideo` when you know the video ID and need metadata such as snippet, statistics, or content details.

Use `videos_searchVideos` when the user wants discovery by topic, title fragment, or general query.

Prefer `videos_getVideo` over search if the user already supplied a valid video ID. Search results are inherently ambiguous and may return the wrong clip.

### Channels

Use `channels_getChannel` when you know the channel ID and need metadata such as subscriber count, branding, or snippet data.

Use `channels_searchChannels` when the user is searching by name, handle, or keyword and does not know the exact channel ID.

Use `channels_listVideos` when the user wants the latest uploads from a specific channel.

### Playlists

Use `playlists_getPlaylist` when you know the playlist ID and need playlist metadata.

Use `playlists_getPlaylistItems` when the user wants the contents of a playlist.

### Transcripts

Use `transcripts_getTranscript` when the user wants subtitles, spoken content, a transcript summary, timestamped quotes, or translation help.

This tool does not consume official YouTube API quota, so it is the best first choice for speech-based questions about a video.

## Practical workflow

Follow this sequence when answering a user request:

1. Identify the resource type: video, channel, playlist, or transcript.
2. Convert URLs or handles into the most direct identifier you can.
3. Choose the narrowest tool that can answer the question.
4. Request only the parts or result count you need.
5. Summarize the returned JSON for the user in plain language.

## Query shaping

Keep requests as narrow as possible:

- Use specific IDs instead of topic searches when possible.
- Use `max_results` only as large as needed.
- Use `parts` only when the user actually needs those fields.
- If the output is getting too large, reduce the scope rather than asking the server to dump everything.

That matters because the server serializes results to JSON strings and truncates long responses. A narrower query is usually better than a broader one.

## Response handling

When reporting results back to the user:

- Cite the exact title, ID, channel name, or playlist name you found.
- Distinguish clearly between "found via search" and "looked up by exact ID".
- Do not invent fields that were not returned.
- If the response appears truncated, say so and rerun with a narrower request.

For transcript tasks, include timestamps when they help the user orient themselves. If the user asked for a quote, keep the quote short and attribute it to the video and timestamp.

## Failure handling

Expect a few common failure modes:

- If search returns the wrong resource, refine the query or switch to exact ID lookup.
- If transcript retrieval fails because transcripts are disabled or unavailable, say that clearly and do not fabricate subtitles.
- If the server reports quota exhaustion, remember that the client pool already rotates API keys automatically. Retry only with a more specific query, or report that all keys are exhausted if the error persists.

## Good defaults

Prefer these defaults unless the user asks otherwise:

- Search by topic first when the user does not know the ID.
- Look up by ID when the ID is known.
- Use transcript data for "what was said" questions.
- Use channel uploads for "what did this creator post recently" questions.
- Use playlist items for "what's inside this playlist" questions.

## Example patterns

### Example 1: Find a video from a vague description

User: "Find the YouTube video where the creator explains how they built the home lab with the mini rack."

Action:

- Search videos with the most specific phrasing available.
- Return a short shortlist with titles, channels, and IDs.

### Example 2: Inspect a known video

User: "Check this video ID and tell me if it has enough details for a summary: `dQw4w9WgXcQ`."

Action:

- Call `videos_getVideo`.
- Summarize title, channel, publish date, duration, and engagement stats if present.

### Example 3: Get recent uploads from a channel

User: "What has this channel uploaded in the last few days?"

Action:

- Resolve the channel ID if needed.
- Call `channels_listVideos`.
- Sort or summarize the returned items by publish date.

### Example 4: Summarize spoken content

User: "Pull the transcript and tell me the part where they talk about pricing."

Action:

- Call `transcripts_getTranscript`.
- Scan the transcript for the relevant segment.
- Answer with the relevant timestamped excerpt and a concise summary.

## Output style

Keep the final answer useful and compact:

- Start with the answer, not the tool process.
- Mention the exact video, channel, or playlist that was used.
- Add bullets only when they improve clarity.
- If the user asked for a follow-up action, offer the next step only after the main answer is complete.

## Mental model

Think of this server as a YouTube research assistant with four lenses:

- Search for discovery
- Get for exact metadata
- List for channel or playlist contents
- Transcript for spoken content

If you keep that mapping in mind, the tool choice is usually obvious.
