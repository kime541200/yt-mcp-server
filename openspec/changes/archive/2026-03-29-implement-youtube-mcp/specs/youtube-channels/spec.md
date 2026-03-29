## ADDED Requirements

### Requirement: Get Channel Details
The system SHALL provide a `channels_getChannel` tool to retrieve basic information and statistics for a single channel.

#### Scenario: Looking up channel info
- **WHEN** the tool is called with a `channelId`
- **THEN** the system returns the channel's snippet, statistics, and branding info.

### Requirement: Search Channels
The system SHALL provide a `channels_searchChannels` tool to discover channels by query.

#### Scenario: Searching by query handle
- **WHEN** the tool is called with `query="@mkbhd"`
- **THEN** the system returns a list of resulting channels.
