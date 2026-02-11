"""Main Typer application and global options."""

from typing import Optional

import typer

from . import __version__
from .commands import (
    activities,
    api,
    auth,
    body,
    devices,
    gear,
    goals,
    health,
    heart,
    hydration,
    menstrual,
    metrics,
    sleep,
    stress,
    vitals,
    workouts,
)

app = typer.Typer(
    name="gc",
    help="CLI to read health data from Garmin Connect.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"gc {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Garmin Connect CLI."""


# Register command groups
app.command("login")(auth.login)
app.command("logout")(auth.logout)
app.command("status")(auth.status)

app.command("health")(health.health)
app.command("steps")(health.steps)
app.command("floors")(health.floors)
app.command("intensity")(health.intensity)
app.command("events")(health.events)

app.add_typer(heart.app, name="heart", help="Heart rate data.")
app.command("sleep")(sleep.sleep_cmd)

app.add_typer(stress.app, name="stress", help="Stress & body battery data.")
app.command("battery")(stress.battery)

app.command("respiration")(vitals.respiration)
app.command("spo2")(vitals.spo2)
app.command("blood-pressure")(vitals.blood_pressure)
app.command("lifestyle")(vitals.lifestyle)

app.add_typer(activities.app, name="activities", help="Activities data.")

app.add_typer(body.app, name="body", help="Body composition & weight data.")

app.add_typer(metrics.app, name="metrics", help="Advanced metrics.")

app.command("hydration")(hydration.hydration)

app.add_typer(devices.app, name="devices", help="Device information.")

app.command("records")(goals.records)
app.add_typer(goals.goals_app, name="goals", help="Goals.")
app.add_typer(goals.badges_app, name="badges", help="Badges.")
app.add_typer(goals.challenges_app, name="challenges", help="Challenges.")

app.add_typer(gear.app, name="gear", help="Gear management.")

app.add_typer(workouts.app, name="workouts", help="Workouts.")
app.add_typer(
    workouts.training_plans_app, name="training-plans", help="Training plans."
)

app.add_typer(menstrual.app, name="menstrual", help="Menstrual cycle data.")
app.add_typer(api.app, name="api", help="Raw Garmin Connect API calls.")
