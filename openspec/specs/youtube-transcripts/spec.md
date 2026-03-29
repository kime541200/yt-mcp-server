## ADDED Requirements

### Requirement: Get Video Transcript
The system SHALL provide a `transcripts_getTranscript` tool that fetches transcript content without expending YouTube API quotas.

#### Scenario: Fetching English transcript for a video
- **WHEN** the user calls the tool with a valid `videoId` and `language="en"`
- **THEN** the system downloads and returns the textual transcript data.

#### Scenario: Searching within a transcript
- **WHEN** the user specifies a keyword to search within the fetched transcript
- **THEN** the system filters the transcript to return the segments matching the keyword along with timestamps.
