"""Custom exceptions for garmincli."""


class GarminCliError(Exception):
    """Base exception for garmincli."""


class AuthenticationError(GarminCliError):
    """Raised when authentication fails."""


class ConnectionError(GarminCliError):
    """Raised when a connection error occurs."""


class RateLimitError(GarminCliError):
    """Raised when rate limit is exceeded."""
