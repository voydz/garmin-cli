"""Goals, records, badges, and challenges commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, render

goals_app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
badges_app = typer.Typer(no_args_is_help=True)
challenges_app = typer.Typer(no_args_is_help=True)


def records(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show personal records."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_personal_record)
        render(data, fmt=fmt, title="Personal Records", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@goals_app.callback(invoke_without_command=True)
def goals_cmd(
    ctx: typer.Context,
    status: str = typer.Option(
        "active", "--status", "-s", help="Goal status (active/future/past)."
    ),
    limit: int = typer.Option(30, "--limit", "-l", help="Number of goals."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show goals."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_goals, status, 0, limit)
        render(data, fmt=fmt, title=f"Goals ({status})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@badges_app.command()
def earned(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show earned badges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_earned_badges)
        render(data, fmt=fmt, title="Earned Badges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@badges_app.command()
def available(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show available badges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_available_badges)
        render(data, fmt=fmt, title="Available Badges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@badges_app.command("in-progress")
def in_progress(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show in-progress badges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_in_progress_badges)
        render(data, fmt=fmt, title="In-Progress Badges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@challenges_app.command()
def adhoc(
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of challenges."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show adhoc challenges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_adhoc_challenges, start_offset, limit)
        render(data, fmt=fmt, title="Adhoc Challenges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@challenges_app.command()
def badge(
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of challenges."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show badge challenges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_badge_challenges, start_offset, limit)
        render(data, fmt=fmt, title="Badge Challenges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@challenges_app.command("available")
def challenges_available(
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of challenges."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show available badge challenges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_available_badge_challenges, start_offset, limit)
        render(data, fmt=fmt, title="Available Badge Challenges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@challenges_app.command("non-completed")
def non_completed(
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of challenges."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show non-completed badge challenges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_non_completed_badge_challenges, start_offset, limit)
        render(data, fmt=fmt, title="Non-Completed Badge Challenges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@challenges_app.command("virtual")
def virtual(
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of challenges."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show in-progress virtual challenges."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_inprogress_virtual_challenges, start_offset, limit)
        render(data, fmt=fmt, title="Virtual Challenges", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
