"""Authentication and token management."""

import os
import shutil
import sys
from pathlib import Path
from typing import Optional

from garminconnect import Garmin

from .errors import AuthenticationError


def get_token_dir(tokenstore: Optional[str] = None) -> Path:
    """Resolve the token storage directory.

    Priority:
    1. Explicit --tokenstore argument
    2. GARMINTOKENS environment variable
    3. If running as PyInstaller binary: .gc-tokens/ relative to binary
    4. Fallback: ~/.garmin-cli/tokens/
    """
    if tokenstore:
        return Path(tokenstore).expanduser().resolve()

    env = os.environ.get("GARMINTOKENS")
    if env:
        return Path(env).expanduser().resolve()

    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / ".gc-tokens"

    return Path.home() / ".garmin-cli" / "tokens"


def login(
    email: str,
    password: str,
    mfa_code: Optional[str] = None,
    wait_mfa: bool = False,
    tokenstore: Optional[str] = None,
) -> Garmin:
    """Authenticate with Garmin Connect and save tokens."""
    token_dir = get_token_dir(tokenstore)

    if wait_mfa:
        prompt_mfa = lambda: input("Enter MFA code: ")  # noqa: E731
        client = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)
    elif mfa_code:
        client = Garmin(email=email, password=password, return_on_mfa=True)
    else:
        client = Garmin(email=email, password=password)

    try:
        result = client.login()

        if mfa_code and result and result[0]:
            # MFA was required, resume with provided code
            client_state = {"oauth1_token": result[0], "oauth2_token": result[1]}
            client.resume_login(client_state, mfa_code)

    except Exception as e:
        raise AuthenticationError(str(e)) from e

    # Save tokens
    token_dir.mkdir(parents=True, exist_ok=True)
    client.garth.dump(str(token_dir))

    return client


def load_client(tokenstore: Optional[str] = None) -> Garmin:
    """Load a Garmin client from saved tokens."""
    token_dir = get_token_dir(tokenstore)

    if not token_dir.exists():
        raise AuthenticationError("Not logged in. Run 'gc login' first.")

    client = Garmin()
    try:
        client.login(tokenstore=str(token_dir))
    except FileNotFoundError:
        raise AuthenticationError("Token files not found. Run 'gc login' first.")
    except Exception as e:
        raise AuthenticationError(f"Failed to load session: {e}") from e

    return client


def logout(tokenstore: Optional[str] = None) -> None:
    """Remove saved tokens."""
    token_dir = get_token_dir(tokenstore)
    if token_dir.exists():
        shutil.rmtree(token_dir)
