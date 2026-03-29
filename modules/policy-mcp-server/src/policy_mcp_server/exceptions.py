class PolicyMCPError(Exception):
    """Base exception for Policy MCP errors."""


class WorkspaceError(PolicyMCPError):
    """Raised when workspace or task directory operations fail."""


class SectionError(PolicyMCPError):
    """Raised when section read operations fail."""


class FindingError(PolicyMCPError):
    """Raised when finding save/load operations fail."""


class SearchError(PolicyMCPError):
    """Raised when search operations fail."""


class EntityListError(PolicyMCPError):
    """Raised when entity list loading fails."""


class CleanupError(PolicyMCPError):
    """Raised when cleanup operations fail."""
