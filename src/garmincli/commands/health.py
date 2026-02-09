"""Health, steps, floors, intensity, events commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render


def health(
    date_shortcut: Optional[str] = typer.Argument(
        None, help="Date shortcut or YYYY-MM-DD."
    ),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show daily health summary."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, start, end)
        data = api_call(client.get_user_summary, cdate)
        render(data, fmt=fmt, title=f"Health Summary ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def steps(
    date_shortcut: Optional[str] = typer.Argument(
        None, help="Date shortcut or YYYY-MM-DD."
    ),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    weekly: bool = typer.Option(False, "--weekly", help="Show weekly stats."),
    weeks: int = typer.Option(4, "--weeks", help="Number of weeks for weekly stats."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show step count data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, start, end)

        if weekly:
            data = api_call(client.get_weekly_steps, cdate, weeks)
            render(data, fmt=fmt, title="Weekly Steps", output=output)
        elif end_date:
            data = api_call(client.get_daily_steps, cdate, end_date)
            render(
                data,
                fmt=fmt,
                title=f"Daily Steps ({cdate} to {end_date})",
                output=output,
            )
        else:
            data = api_call(client.get_steps_data, cdate)
            render(data, fmt=fmt, title=f"Steps ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def floors(
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
    """Show floors climbed data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_floors, cdate)
        render(data, fmt=fmt, title=f"Floors ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def intensity(
    date_shortcut: Optional[str] = typer.Argument(
        None, help="Date shortcut or YYYY-MM-DD."
    ),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    weekly: bool = typer.Option(False, "--weekly", help="Show weekly stats."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    weeks: int = typer.Option(4, "--weeks", help="Number of weeks for weekly stats."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show intensity minutes data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, start, end)

        if weekly:
            data = api_call(client.get_weekly_intensity_minutes, cdate, weeks)
            render(data, fmt=fmt, title="Weekly Intensity Minutes", output=output)
        else:
            data = api_call(client.get_intensity_minutes_data, cdate)
            render(data, fmt=fmt, title=f"Intensity Minutes ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def events(
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
    """Show daily events (auto-detected activities, etc.)."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_all_day_events, cdate)
        render(data, fmt=fmt, title=f"Events ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
