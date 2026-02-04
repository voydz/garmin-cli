"""Custom exceptions for Garmin CLI."""


class GarminCliError(Exception):
    """Base exception for Garmin CLI."""


class AuthenticationError(GarminCliError):
    """Raised when authentication fails."""


class ConnectionError(GarminCliError):
    """Raised when a connection error occurs."""


class RateLimitError(GarminCliError):
    """Raised when rate limit is exceeded."""
