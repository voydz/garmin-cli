"""Authentication commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import get_token_dir
from ..auth import load_client as _load_client
from ..auth import login as _login
from ..auth import logout as _logout
from ..errors import GarminCliError
from ..output import print_error, print_success, render


def login(
    email: str = typer.Option(
        ..., "--email", "-e", help="Garmin Connect email.", envvar="GARMIN_EMAIL"
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        help="Garmin Connect password.",
        envvar="GARMIN_PASSWORD",
    ),
    mfa: Optional[str] = typer.Option(None, "--mfa", help="MFA code."),
    wait_mfa: bool = typer.Option(
        False, "--wait-mfa", help="Wait for MFA code from stdin."
    ),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
) -> None:
    """Log in to Garmin Connect."""
    try:
        client = _login(
            email, password, mfa_code=mfa, wait_mfa=wait_mfa, tokenstore=tokenstore
        )
        name = client.get_full_name() or client.display_name or "User"
        print_success(f"Logged in as {name}.")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def logout(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
) -> None:
    """Log out and remove saved tokens."""
    _logout(tokenstore=tokenstore)
    print_success("Logged out.")


def status(
    profile: bool = typer.Option(False, "--profile", help="Show full profile."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option(
        "table", "--format", "-f", help="Output format (table/json)."
    ),
) -> None:
    """Show login status and optionally user profile."""
    try:
        client = _load_client(tokenstore=tokenstore)
        if profile:
            data = api_call(client.get_user_profile)
            render(data, fmt=fmt, title="User Profile")
        else:
            info = {
                "Status": "Logged in",
                "Display Name": client.display_name or "-",
                "Full Name": client.get_full_name() or "-",
                "Unit System": client.get_unit_system() or "-",
                "Token Store": str(get_token_dir(tokenstore)),
            }
            render(info, fmt=fmt, title="Login Status")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
