"""Device commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def devices_cmd(
    ctx: typer.Context,
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """List devices."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_devices)
        render(data, fmt=fmt, title="Devices", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("last-used")
def last_used(
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show last used device."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_device_last_used)
        render(data, fmt=fmt, title="Last Used Device", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def primary(
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show primary training device."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_primary_training_device)
        render(data, fmt=fmt, title="Primary Training Device", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def settings(
    device_id: str = typer.Argument(..., help="Device ID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show device settings."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_device_settings, device_id)
        render(data, fmt=fmt, title=f"Device Settings ({device_id})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def alarms(
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show device alarms."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_device_alarms)
        render(data, fmt=fmt, title="Device Alarms", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def solar(
    device_id: str = typer.Argument(..., help="Device ID."),
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show solar data for a device."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, end=end)
        data = api_call(client.get_device_solar_data, device_id, cdate, end_date)
        render(data, fmt=fmt, title=f"Solar Data ({device_id})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
