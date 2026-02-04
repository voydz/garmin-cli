"""Workouts and training plans commands."""

from typing import Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, print_success, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
training_plans_app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


@app.callback(invoke_without_command=True)
def workouts_cmd(
    ctx: typer.Context,
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of workouts."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """List workouts."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_workouts, start_offset, limit)
        render(data, fmt=fmt, title="Workouts", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def get(
    workout_id: str = typer.Argument(..., help="Workout ID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Get workout by ID."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_workout_by_id, workout_id)
        render(data, fmt=fmt, title=f"Workout {workout_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def download(
    workout_id: str = typer.Argument(..., help="Workout ID."),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
) -> None:
    """Download workout as FIT file."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.download_workout, workout_id)
        filename = output_file or f"workout_{workout_id}.fit"
        with open(filename, "wb") as f:
            f.write(data)
        print_success(f"Downloaded to {filename}")
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def scheduled(
    workout_id: str = typer.Argument(..., help="Scheduled workout ID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Get scheduled workout by ID."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_scheduled_workout_by_id, workout_id)
        render(data, fmt=fmt, title=f"Scheduled Workout {workout_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@training_plans_app.callback(invoke_without_command=True)
def training_plans_cmd(
    ctx: typer.Context,
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """List training plans."""
    if ctx.invoked_subcommand is not None:
        return
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_training_plans)
        render(data, fmt=fmt, title="Training Plans", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@training_plans_app.command("get")
def get_plan(
    plan_id: str = typer.Argument(..., help="Training plan ID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Get training plan by ID."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_training_plan_by_id, plan_id)
        render(data, fmt=fmt, title=f"Training Plan {plan_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@training_plans_app.command()
def adaptive(
    plan_id: str = typer.Argument(..., help="Training plan ID."),
    tokenstore: Optional[str] = typer.Option(None, "--tokenstore", help="Token storage path."),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Get adaptive training plan by ID."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = api_call(client.get_adaptive_training_plan_by_id, plan_id)
        render(data, fmt=fmt, title=f"Adaptive Training Plan {plan_id}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
