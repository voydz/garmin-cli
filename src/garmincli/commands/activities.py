"""Activities commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..dates import resolve_date
from ..errors import GarminCliError
from ..output import print_error, print_success, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

ACTIVITY_LIST_COLUMNS = [
    "activityId",
    "activityName",
    "activityType",
    "startTimeLocal",
    "distance",
    "duration",
    "averageHR",
]


@app.callback(invoke_without_command=True)
def activities_cmd(
    ctx: typer.Context,
    date: Optional[str] = typer.Option(
        None, "--date", "-d", help="Date shortcut or YYYY-MM-DD."
    ),
    start: Optional[str] = typer.Option(None, "--start", help="Start date."),
    end: Optional[str] = typer.Option(None, "--end", help="End date."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of activities."),
    offset: int = typer.Option(0, "--offset", help="Starting offset."),
    activity_type: Optional[str] = typer.Option(
        None, "--type", "-t", help="Activity type filter."
    ),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """List activities."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)

        if date:
            cdate, end_date = resolve_date(date_str=date)
            data = api_call(client.get_activities_fordate, cdate)
        elif start and end:
            data = api_call(client.get_activities_by_date, start, end, activity_type)
        else:
            data = api_call(client.get_activities, offset, limit, activity_type)

        render(data, fmt=fmt, title="Activities", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def last(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show last activity."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_last_activity)
        render(data, fmt=fmt, title="Last Activity", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def get(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Get activity by ID."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity, activity_id)
        render(data, fmt=fmt, title=f"Activity {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def count(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
) -> None:
    """Show total activity count."""
    try:
        client = load_client(tokenstore=tokenstore)
        total = api_call(client.count_activities)
        if fmt == "json":
            render({"totalCount": total}, fmt=fmt)
        else:
            typer.echo(f"Total activities: {total}")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def details(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity details."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_details, activity_id)
        render(data, fmt=fmt, title=f"Activity Details {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def splits(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity splits."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_splits, activity_id)
        render(data, fmt=fmt, title=f"Splits {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("typed-splits")
def typed_splits(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show typed activity splits."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_typed_splits, activity_id)
        render(data, fmt=fmt, title=f"Typed Splits {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("split-summaries")
def split_summaries(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity split summaries."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_split_summaries, activity_id)
        render(data, fmt=fmt, title=f"Split Summaries {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def weather(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity weather."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_weather, activity_id)
        render(data, fmt=fmt, title=f"Weather {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("hr-zones")
def hr_zones(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity heart rate zones."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_hr_in_timezones, activity_id)
        render(data, fmt=fmt, title=f"HR Zones {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("power-zones")
def power_zones(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity power zones."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_power_in_timezones, activity_id)
        render(data, fmt=fmt, title=f"Power Zones {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("exercise-sets")
def exercise_sets(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity exercise sets."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_exercise_sets, activity_id)
        render(data, fmt=fmt, title=f"Exercise Sets {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("types")
def activity_types(
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show available activity types."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_types)
        render(data, fmt=fmt, title="Activity Types", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def download(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    dl_format: str = typer.Option(
        "fit", "--format", "-f", help="Download format (fit/tcx/gpx/kml/csv)."
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path."
    ),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
) -> None:
    """Download an activity file."""
    from garminconnect import Garmin as GarminAPI

    fmt_map = {
        "fit": GarminAPI.ActivityDownloadFormat.ORIGINAL,
        "tcx": GarminAPI.ActivityDownloadFormat.TCX,
        "gpx": GarminAPI.ActivityDownloadFormat.GPX,
        "kml": GarminAPI.ActivityDownloadFormat.KML,
        "csv": GarminAPI.ActivityDownloadFormat.CSV,
    }
    dl_fmt = fmt_map.get(dl_format.lower())
    if not dl_fmt:
        print_error(f"Invalid format: {dl_format}. Use fit/tcx/gpx/kml/csv.")
        raise typer.Exit(1)

    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.download_activity, activity_id, dl_fmt)

        ext = "zip" if dl_format.lower() == "fit" else dl_format.lower()
        filename = output_file or f"activity_{activity_id}.{ext}"

        with open(filename, "wb") as f:
            f.write(data)
        print_success(f"Downloaded to {filename}")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def upload(
    file: str = typer.Argument(..., help="Activity file to upload (.fit, .gpx, .tcx)."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
) -> None:
    """Upload an activity file."""
    try:
        client = load_client(tokenstore=tokenstore)
        result = api_call(client.upload_activity, file)
        print_success(f"Uploaded {file}")
        if result:
            render(result, fmt=fmt, title="Upload Result")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def progress(
    start: str = typer.Option(..., "--start", help="Start date (YYYY-MM-DD)."),
    end: str = typer.Option(..., "--end", help="End date (YYYY-MM-DD)."),
    metric: str = typer.Option(
        "distance", "--metric", "-m", help="Metric (distance/duration/elevation)."
    ),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show activity progress summary."""
    metric_map = {
        "distance": "distance",
        "duration": "duration",
        "elevation": "elevationGain",
    }
    m = metric_map.get(metric, metric)
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_progress_summary_between_dates, start, end, m)
        render(data, fmt=fmt, title=f"Progress ({start} to {end})", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("gear")
def activity_gear(
    activity_id: str = typer.Argument(..., help="Activity ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Show gear used for an activity."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_activity_gear, activity_id)
        render(data, fmt=fmt, title=f"Gear for Activity {activity_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
