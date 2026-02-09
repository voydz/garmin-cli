"""Vitals commands: respiration, SpO2, blood pressure, lifestyle."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render


def respiration(
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
    """Show respiration data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_respiration_data, cdate)
        render(data, fmt=fmt, title=f"Respiration ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def spo2(
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
    """Show SpO2 data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_spo2_data, cdate)
        render(data, fmt=fmt, title=f"SpO2 ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def blood_pressure(
    date_shortcut: Optional[str] = typer.Argument(
        None, help="Date shortcut or YYYY-MM-DD."
    ),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show blood pressure data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, end=end)
        data = api_call(client.get_blood_pressure, cdate, end_date)
        render(data, fmt=fmt, title=f"Blood Pressure ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


def lifestyle(
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
    """Show lifestyle logging data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_lifestyle_logging_data, cdate)
        render(data, fmt=fmt, title=f"Lifestyle ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
