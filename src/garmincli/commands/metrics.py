"""Advanced metrics commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True)


@app.command()
def vo2max(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show VO2 Max data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_max_metrics, cdate)
        render(data, fmt=fmt, title=f"VO2 Max ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def hrv(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show Heart Rate Variability data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_hrv_data, cdate)
        render(data, fmt=fmt, title=f"HRV ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("training-readiness")
def training_readiness(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show training readiness data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_training_readiness, cdate)
        render(data, fmt=fmt, title=f"Training Readiness ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("morning-readiness")
def morning_readiness(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show morning training readiness data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_morning_training_readiness, cdate)
        render(data, fmt=fmt, title=f"Morning Readiness ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("training-status")
def training_status(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show training status data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_training_status, cdate)
        render(data, fmt=fmt, title=f"Training Status ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("fitness-age")
def fitness_age(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show fitness age data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, _ = resolve_date(date_shortcut, date)
        data = api_call(client.get_fitnessage_data, cdate)
        render(data, fmt=fmt, title=f"Fitness Age ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("race-predictions")
def race_predictions(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    prediction_type: Optional[str] = typer.Option(None, "--type", "-t", help="Type (daily/monthly)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show race predictions."""
    try:
        client = load_client(tokenstore=tokenstore)
        if start and end and prediction_type:
            data = api_call(client.get_race_predictions, start, end, prediction_type)
        else:
            data = api_call(client.get_race_predictions)
        render(data, fmt=fmt, title="Race Predictions", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("endurance-score")
def endurance_score(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    end: Optional[str] = typer.Option(None, "--end", help="End date for range."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show endurance score data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, end=end)
        data = api_call(client.get_endurance_score, cdate, end_date)
        render(data, fmt=fmt, title=f"Endurance Score ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("hill-score")
def hill_score(
    date_shortcut: Optional[str] = typer.Argument(None, help="Date shortcut or YYYY-MM-DD."),
    date: Optional[str] = typer.Option(None, "--date", "-d", help="Date (YYYY-MM-DD)."),
    end: Optional[str] = typer.Option(None, "--end", help="End date for range."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show hill score data."""
    try:
        client = load_client(tokenstore=tokenstore)
        cdate, end_date = resolve_date(date_shortcut, date, end=end)
        data = api_call(client.get_hill_score, cdate, end_date)
        render(data, fmt=fmt, title=f"Hill Score ({cdate})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("lactate-threshold")
def lactate_threshold(
    latest: bool = typer.Option(True, "--latest/--no-latest", help="Get latest data."),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    aggregation: str = typer.Option("daily", "--aggregation", "-a", help="Aggregation (daily/weekly/monthly/yearly)."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show lactate threshold data."""
    try:
        client = load_client(tokenstore=tokenstore)
        if start:
            data = api_call(
                client.get_lactate_threshold,
                latest=False,
                start_date=start,
                end_date=end,
                aggregation=aggregation,
            )
        else:
            data = api_call(client.get_lactate_threshold, latest=True)
        render(data, fmt=fmt, title="Lactate Threshold", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("cycling-ftp")
def cycling_ftp(
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show cycling FTP data."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_cycling_ftp)
        render(data, fmt=fmt, title="Cycling FTP", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
