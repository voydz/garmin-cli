"""Garmin API wrapper with error handling."""

from typing import Any, Callable

from garminconnect import (
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from .errors import AuthenticationError, ConnectionError, GarminCliError, RateLimitError


def api_call(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Execute a Garmin API call with standardized error handling."""
    try:
        return func(*args, **kwargs)
    except GarminConnectAuthenticationError as e:
        raise AuthenticationError(
            f"Authentication failed. Try 'gc login' again. ({e})"
        ) from e
    except GarminConnectTooManyRequestsError as e:
        raise RateLimitError(
            f"Rate limit exceeded. Wait a moment and try again. ({e})"
        ) from e
    except GarminConnectConnectionError as e:
        raise ConnectionError(f"Connection error: {e}") from e
    except Exception as e:
        raise GarminCliError(f"Unexpected error: {e}") from e
