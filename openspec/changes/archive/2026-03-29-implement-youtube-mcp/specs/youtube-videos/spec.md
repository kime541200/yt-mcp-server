## ADDED Requirements

### Requirement: Fetch Video Details
The system SHALL provide a `videos_getVideo` tool that accepts a YouTube video ID and returns the video's snippet, contentDetails, and statistics.

#### Scenario: Successfully fetching video details
- **WHEN** the tool is called with a valid `videoId`
- **THEN** the system returns a JSON object containing the video's details.

### Requirement: Search Videos
The system SHALL provide a `videos_searchVideos` tool to search YouTube videos with parameters like query, maxResults, and publishedAfter.

#### Scenario: Searching for specific topic
- **WHEN** the user calls the search tool with `query="python fastmcp"`
- **THEN** the system returns a list of videos matching the query up to the maxResults limit.
