"""Workouts and training plans commands."""

import inspect
import json
from typing import Any, Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, print_success, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
training_plans_app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

STEP_TYPE_IDS = {
    "warmup": 1,
    "cooldown": 2,
    "interval": 3,
}

TARGET_TYPE_IDS = {
    "no.target": 1,
    "heart.rate.zone": 4,
}


def _extract_sport_info(item: dict[str, Any]) -> tuple[Optional[str], Optional[int]]:
    sport = item.get("sportType")
    if isinstance(sport, dict):
        return sport.get("sportTypeKey"), sport.get("sportTypeId")

    key = item.get("sportTypeKey") or item.get("typeKey") or item.get("key")
    sport_id = item.get("sportTypeId") or item.get("typeId") or item.get("id")
    if not key:
        name = item.get("typeName") or item.get("name")
        if isinstance(name, str):
            key = name.lower()
    return key, sport_id


def _iter_type_items(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("workoutTypes", "activityTypes", "types", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        values = [value for value in data.values() if isinstance(value, dict)]
        if values:
            return values
    return []


def _resolve_sport_id(client: Any, sport_key: str) -> Optional[int]:
    for getter_name in ("get_workout_types", "get_activity_types"):
        getter = getattr(client, getter_name, None)
        if getter is None:
            continue
        try:
            data = api_call(getter)
        except GarminCliError:
            continue
        for item in _iter_type_items(data):
            key, sport_id = _extract_sport_info(item)
            if not key or sport_id is None:
                continue
            if key.lower() == sport_key.lower():
                return sport_id
    return None


def _parse_steps(steps_raw: str) -> list[dict[str, Any]]:
    try:
        steps = json.loads(steps_raw)
    except json.JSONDecodeError as exc:
        raise GarminCliError(f"Invalid steps JSON: {exc}") from exc
    if not isinstance(steps, list) or not steps:
        raise GarminCliError("Steps must be a non-empty JSON array.")

    first = steps[0]
    if isinstance(first, dict) and (
        "stepType" in first or "stepTypeKey" in first or "endCondition" in first
    ):
        normalized: list[dict[str, Any]] = []
        for idx, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise GarminCliError("Each step must be a JSON object.")
            entry = dict(step)
            entry.setdefault("stepOrder", idx)
            normalized.append(entry)
        return normalized

    normalized_steps: list[dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise GarminCliError("Each step must be a JSON object.")
        step_type_key = step.get("type")
        duration = step.get("duration")
        if not step_type_key or duration is None:
            raise GarminCliError("Each step requires 'type' and 'duration' fields.")

        step_type = {"stepTypeKey": step_type_key}
        step_type_id = STEP_TYPE_IDS.get(str(step_type_key).lower())
        if step_type_id is not None:
            step_type["stepTypeId"] = step_type_id

        end_condition = {"conditionTypeKey": "time", "conditionTypeId": 2}

        target = step.get("target")
        target_key = "no.target"
        zone_number: Optional[int] = None
        if target:
            target_text = str(target)
            if target_text.startswith("hr_zone:"):
                target_key = "heart.rate.zone"
                try:
                    zone_number = int(target_text.split(":", 1)[1])
                except ValueError as exc:
                    raise GarminCliError(
                        f"Invalid hr_zone target: {target_text}"
                    ) from exc
            elif target_text in ("none", "no.target"):
                target_key = "no.target"
            else:
                raise GarminCliError(f"Unsupported target format: {target_text}")

        target_type = {
            "workoutTargetTypeKey": target_key,
            "workoutTargetTypeId": TARGET_TYPE_IDS.get(target_key),
        }
        if target_type["workoutTargetTypeId"] is None:
            target_type.pop("workoutTargetTypeId")

        try:
            end_value = float(duration)
        except (TypeError, ValueError) as exc:
            raise GarminCliError(
                f"Invalid duration for step {idx}: {duration}"
            ) from exc

        entry = {
            "stepOrder": idx,
            "stepType": step_type,
            "endCondition": end_condition,
            "endConditionValue": end_value,
            "targetType": target_type,
        }
        if zone_number is not None:
            entry["zoneNumber"] = zone_number
        normalized_steps.append(entry)

    return normalized_steps


def _build_workout_payload(
    client: Any,
    name: Optional[str],
    sport_key: Optional[str],
    sport_id: Optional[int],
    steps_raw: Optional[str],
    file_path: Optional[str],
) -> dict[str, Any]:
    if file_path:
        try:
            with open(file_path, "r") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise GarminCliError(f"Invalid workout JSON file: {exc}") from exc

    if not name or not sport_key or not steps_raw:
        raise GarminCliError("Provide --file or --name, --sport, and --steps.")

    resolved_id = sport_id or _resolve_sport_id(client, sport_key)
    if resolved_id is None:
        raise GarminCliError(
            f"Unable to resolve sport id for '{sport_key}'. Use --sport-id or --file."
        )

    sport = {"sportTypeKey": sport_key, "sportTypeId": resolved_id}
    steps = _parse_steps(steps_raw)

    return {
        "workoutName": name,
        "sportType": sport,
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": sport,
                "workoutSteps": steps,
            }
        ],
    }


def _call_connectapi(connectapi: Any, path: str, method: str, payload: Any) -> Any:
    try:
        sig = inspect.signature(connectapi)
    except (TypeError, ValueError):
        if method != "GET":
            raise GarminCliError("Garmin connectapi does not support non-GET methods.")
        return connectapi(path)

    kwargs: dict[str, Any] = {}
    if "method" in sig.parameters:
        kwargs["method"] = method
    elif "http_method" in sig.parameters:
        kwargs["http_method"] = method
    elif method != "GET":
        raise GarminCliError("Garmin connectapi does not support non-GET methods.")

    if payload is not None:
        if "json" in sig.parameters:
            kwargs["json"] = payload
        elif "data" in sig.parameters:
            kwargs["data"] = payload

    return connectapi(path, **kwargs)


def _request_with_session(session: Any, method: str, url: str, payload: Any) -> Any:
    if not hasattr(session, "request"):
        raise GarminCliError("Garmin session does not support request().")
    try:
        response = session.request(method, url, json=payload)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        if hasattr(response, "json"):
            try:
                return response.json()
            except Exception:
                return getattr(response, "text", response)
        return response
    except Exception as exc:
        raise GarminCliError(f"Workout request failed: {exc}") from exc


def _workout_request(client: Any, method: str, path: str, payload: Any = None) -> Any:
    garth = getattr(client, "garth", None)
    if garth and hasattr(garth, "connectapi"):
        try:
            return _call_connectapi(garth.connectapi, path, method, payload)
        except (TypeError, GarminCliError):
            pass
    session = None
    for attr in ("session", "_session", "client"):
        if garth and hasattr(garth, attr):
            session = getattr(garth, attr)
            break
    if session:
        url = path if path.startswith("http") else f"https://connect.garmin.com{path}"
        return _request_with_session(session, method, url, payload)
    raise GarminCliError("Garmin client does not support workout write requests.")


@app.callback(invoke_without_command=True)
def workouts_cmd(
    ctx: typer.Context,
    start_offset: int = typer.Option(0, "--start", help="Starting offset."),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of workouts."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path."
    ),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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


@app.command()
def create(
    name: Optional[str] = typer.Option(None, "--name", help="Workout name."),
    sport: Optional[str] = typer.Option(
        None, "--sport", help="Sport type key (e.g. cycling)."
    ),
    sport_id: Optional[int] = typer.Option(None, "--sport-id", help="Sport type ID."),
    steps: Optional[str] = typer.Option(None, "--steps", help="Workout steps JSON."),
    file: Optional[str] = typer.Option(None, "--file", help="Workout JSON file."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Create a workout."""
    try:
        client = load_client(tokenstore=tokenstore)
        payload = _build_workout_payload(client, name, sport, sport_id, steps, file)
        data = _workout_request(client, "POST", "/workout-service/workout", payload)
        if data is None:
            print_success("Workout created.")
        else:
            render(data, fmt=fmt, title="Workout Created", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def update(
    workout_id: str = typer.Argument(..., help="Workout ID."),
    name: Optional[str] = typer.Option(None, "--name", help="Workout name."),
    sport: Optional[str] = typer.Option(
        None, "--sport", help="Sport type key (e.g. cycling)."
    ),
    sport_id: Optional[int] = typer.Option(None, "--sport-id", help="Sport type ID."),
    steps: Optional[str] = typer.Option(None, "--steps", help="Workout steps JSON."),
    file: Optional[str] = typer.Option(None, "--file", help="Workout JSON file."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Update a workout."""
    try:
        client = load_client(tokenstore=tokenstore)
        payload = _build_workout_payload(client, name, sport, sport_id, steps, file)
        payload.setdefault("workoutId", workout_id)
        data = _workout_request(
            client, "PUT", f"/workout-service/workout/{workout_id}", payload
        )
        if data is None:
            print_success(f"Workout {workout_id} updated.")
        else:
            render(
                data, fmt=fmt, title=f"Workout Updated ({workout_id})", output=output
            )
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete")
def delete_workout(
    workout_id: str = typer.Argument(..., help="Workout ID."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Delete a workout."""
    try:
        client = load_client(tokenstore=tokenstore)
        data = _workout_request(
            client, "DELETE", f"/workout-service/workout/{workout_id}"
        )
        if data is None:
            print_success(f"Workout {workout_id} deleted.")
        else:
            render(
                data, fmt=fmt, title=f"Workout Deleted ({workout_id})", output=output
            )
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)


@training_plans_app.callback(invoke_without_command=True)
def training_plans_cmd(
    ctx: typer.Context,
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
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
