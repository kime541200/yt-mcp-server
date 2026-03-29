## ADDED Requirements

### Requirement: Get Playlist Metadata
The system SHALL provide a `playlists_getPlaylist` tool to retrieve the title, description, and metadata of a playlist.

#### Scenario: Retrieving playlist summary
- **WHEN** the tool is called with a `playlistId`
- **THEN** the system returns the playlist snippet information.

### Requirement: Get Playlist Items
The system SHALL provide a `playlists_getPlaylistItems` tool to iterate through videos contained in a playlist.

#### Scenario: Fetching videos in a list
- **WHEN** the tool is called with `playlistId` and a `maxResults` parameter
- **THEN** the system returns the videos residing in the specified playlist.
