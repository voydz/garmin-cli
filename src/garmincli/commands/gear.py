"""Gear commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def gear_cmd(
    ctx: typer.Context,
    user_profile_number: Optional[str] = typer.Argument(None, help="User profile number."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """List gear."""
    if ctx.invoked_subcommand is not None:
        return
    if not user_profile_number:
        print_error("User profile number is required. Find it via 'gc status --profile'.")
        raise typer.Exit(1)
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_gear, user_profile_number)
        render(data, fmt=fmt, title="Gear", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def defaults(
    user_profile_number: str = typer.Argument(..., help="User profile number."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show default gear for activity types."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_gear_defaults, user_profile_number)
        render(data, fmt=fmt, title="Gear Defaults", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def stats(
    gear_uuid: str = typer.Argument(..., help="Gear UUID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show gear statistics."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_gear_stats, gear_uuid)
        render(data, fmt=fmt, title=f"Gear Stats ({gear_uuid})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("activities")
def gear_activities(
    gear_uuid: str = typer.Argument(..., help="Gear UUID."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of activities."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activities for a gear item."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_gear_activities, gear_uuid, limit)
        render(data, fmt=fmt, title=f"Activities for Gear ({gear_uuid})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
