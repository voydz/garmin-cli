"""Menstrual cycle commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def menstrual_cmd(
    ctx: typer.Context,
    date_shortcut: Optional[str] = typer.Argument(
        None, help="Date shortcut or YYYY-MM-DD."
    ),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show menstrual cycle data for a date."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_menstrual_data_for_date, cdate)
        render(data, fmt=fmt, title=f"Menstrual Data ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def calendar(
    start: str = typer.Option(..., "--start", help="Start date (YYYY-MM-DD)."),
    end: str = typer.Option(..., "--end", help="End date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show menstrual calendar data."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_menstrual_calendar_data, start, end)
        render(
            data, fmt=fmt, title=f"Menstrual Calendar ({start} to {end})", output=output
        )
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def pregnancy(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show pregnancy snapshot data."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_pregnancy_summary)
        render(data, fmt=fmt, title="Pregnancy Summary", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
