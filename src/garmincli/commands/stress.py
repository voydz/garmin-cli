"""Stress and body battery commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def stress_cmd(
    ctx: typer.Context,
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    weekly: bool = typer.Option(False, "--weekly", help="Show weekly stats."),
    weeks: int = typer.Option(4, "--weeks", help="Number of weeks for weekly stats."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show stress data."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        if weekly:
            data = api_call(client.get_weekly_stress, cdate, weeks)
            render(data, fmt=fmt, title="Weekly Stress", output=output)
        else:
            data = api_call(client.get_stress_data, cdate)
            render(data, fmt=fmt, title=f"Stress ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("all-day")
def all_day(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show all-day stress data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_all_day_stress, cdate)
        render(data, fmt=fmt, title=f"All-Day Stress ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def battery(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    events: bool = typer.Option(False, "--events", help="Show battery events."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show body battery data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, start, end)
        if events:
            data = api_call(client.get_body_battery_events, cdate)
            render(data, fmt=fmt, title=f"Body Battery Events ({cdate})", output=output)
        else:
            data = api_call(client.get_body_battery, cdate, end_date)
            render(data, fmt=fmt, title=f"Body Battery ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
