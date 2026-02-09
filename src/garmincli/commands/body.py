"""Body composition and weight commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def body_cmd(
    ctx: typer.Context,
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
    """Show body composition data."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, end=end)
        data = api_call(client.get_body_composition, cdate, end_date or cdate)
        render(data, fmt=fmt, title=f"Body Composition ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def weighins(
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
    """Show weigh-in data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, start, end)
        if end_date:
            data = api_call(client.get_weigh_ins, cdate, end_date)
        else:
            data = api_call(client.get_daily_weigh_ins, cdate)
        render(data, fmt=fmt, title="Weigh-ins", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
