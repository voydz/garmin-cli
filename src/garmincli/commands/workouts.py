"""Workouts and training plans commands."""

import inspect
import json
from typing import Any, Optional, Tuple

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, print_success, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
training_plans_app = typer.Typer(no_args_is_help=True, invoke_without_command=True)

TARGET_TYPE_MAP = {
    "hr_zone": "heart.rate.zone",
    "heart_rate_zone": "heart.rate.zone",
    "heartrate_zone": "heart.rate.zone",
    "heart.rate.zone": "heart.rate.zone",
    "power_zone": "power.zone",
    "power.zone": "power.zone",
    "pace_zone": "pace.zone",
    "pace.zone": "pace.zone",
    "cadence": "cadence",
    "heart_rate": "heart.rate",
    "heart.rate": "heart.rate",
    "no_target": "no.target",
    "no.target": "no.target",
    "none": "no.target",
}

SPORT_TYPE_DISPLAY_ORDER = {
    "running": 1,
    "cycling": 2,
    "swimming": 3,
    "walking": 4,
    "multi_sport": 5,
    "fitness_equipment": 6,
    "hiking": 7,
}

STEP_TYPE_META = {
    "warmup": {"stepTypeId": 1, "displayOrder": 1},
    "cooldown": {"stepTypeId": 2, "displayOrder": 2},
    "interval": {"stepTypeId": 3, "displayOrder": 3},
    "recovery": {"stepTypeId": 4, "displayOrder": 4},
    "rest": {"stepTypeId": 5, "displayOrder": 5},
    "repeat": {"stepTypeId": 6, "displayOrder": 6},
}

CONDITION_TYPE_META = {
    "distance": {"conditionTypeId": 1, "displayOrder": 1, "displayable": True},
    "time": {"conditionTypeId": 2, "displayOrder": 2, "displayable": True},
    "heart_rate": {"conditionTypeId": 3, "displayOrder": 3, "displayable": True},
    "calories": {"conditionTypeId": 4, "displayOrder": 4, "displayable": True},
    "cadence": {"conditionTypeId": 5, "displayOrder": 5, "displayable": True},
    "power": {"conditionTypeId": 6, "displayOrder": 6, "displayable": True},
    "iterations": {"conditionTypeId": 7, "displayOrder": 7, "displayable": False},
}

TARGET_TYPE_META = {
    "no.target": {"workoutTargetTypeId": 1, "displayOrder": 1},
    "heart.rate": {"workoutTargetTypeId": 2, "displayOrder": 2},
    "cadence": {"workoutTargetTypeId": 3, "displayOrder": 3},
    "speed": {"workoutTargetTypeId": 4, "displayOrder": 4},
    "power": {"workoutTargetTypeId": 5, "displayOrder": 5},
    "open": {"workoutTargetTypeId": 6, "displayOrder": 6},
    "heart.rate.zone": {"workoutTargetTypeId": 2, "displayOrder": 2},
    "power.zone": {"workoutTargetTypeId": 5, "displayOrder": 5},
    "pace.zone": {"workoutTargetTypeId": 4, "displayOrder": 4},
}


def _parse_steps(steps_raw: str) -> list[dict[str, Any]]:
    try:
        steps = json.loads(steps_raw)
    except json.JSONDecodeError as exc:
        raise GarminCliError(f"Invalid steps JSON: {exc}") from exc
    if not isinstance(steps, list) or not steps:
        raise GarminCliError("Steps must be a non-empty JSON array.")

    normalized: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict):
            raise GarminCliError("Each step must be a JSON object.")
        normalized.append(step)
    return normalized


def _parse_target(target: Any) -> Tuple[str, Optional[float]]:
    if isinstance(target, (int, float)):
        return ("no.target", float(target))
    if not isinstance(target, str):
        raise GarminCliError(
            "Target must be a string like 'hr_zone:2' or a Garmin targetType object."
        )

    raw = target.strip()
    if not raw:
        raise GarminCliError("Target must not be empty.")

    if ":" in raw:
        kind, value = raw.split(":", 1)
        kind = kind.strip().lower()
        value = value.strip()
    else:
        kind, value = raw.lower(), ""

    target_type = TARGET_TYPE_MAP.get(kind)
    if not target_type:
        raise GarminCliError(
            f"Unknown target '{target}'. Use Garmin-shaped steps or a supported "
            "shortcut like 'hr_zone:2'."
        )

    if not value:
        return (target_type, None)
    try:
        parsed_value = float(value) if "." in value else int(value)
    except ValueError as exc:
        raise GarminCliError(f"Target value must be numeric (got '{value}').") from exc
    return (target_type, parsed_value)


def _build_step_type(step_type: dict[str, Any]) -> dict[str, Any]:
    step_type_key = step_type.get("stepTypeKey")
    if isinstance(step_type_key, str):
        step_type_key = step_type_key.lower()
        step_type["stepTypeKey"] = step_type_key
        meta = STEP_TYPE_META.get(step_type_key)
        if meta:
            step_type.setdefault("stepTypeId", meta["stepTypeId"])
            step_type.setdefault("displayOrder", meta["displayOrder"])
    return step_type


def _build_end_condition(end_condition: dict[str, Any]) -> dict[str, Any]:
    condition_key = end_condition.get("conditionTypeKey")
    if isinstance(condition_key, str):
        condition_key = condition_key.lower()
        end_condition["conditionTypeKey"] = condition_key
        meta = CONDITION_TYPE_META.get(condition_key)
        if meta:
            end_condition.setdefault("conditionTypeId", meta["conditionTypeId"])
            end_condition.setdefault("displayOrder", meta["displayOrder"])
            end_condition.setdefault("displayable", meta["displayable"])
    return end_condition


def _build_target_type(target_type: dict[str, Any]) -> dict[str, Any]:
    target_key = target_type.get("workoutTargetTypeKey")
    if isinstance(target_key, str):
        target_key = target_key.lower()
        target_type["workoutTargetTypeKey"] = target_key
        meta = TARGET_TYPE_META.get(target_key)
        if meta:
            target_type.setdefault("workoutTargetTypeId", meta["workoutTargetTypeId"])
            target_type.setdefault("displayOrder", meta["displayOrder"])
    return target_type


def _normalize_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise GarminCliError("Each step must be a JSON object.")
        current = dict(step)

        step_type = current.get("stepType")
        if step_type is None and "type" in current:
            step_type = {"stepTypeKey": current.pop("type")}
        if isinstance(step_type, str):
            step_type = {"stepTypeKey": step_type}
        if not isinstance(step_type, dict) or "stepTypeKey" not in step_type:
            raise GarminCliError(
                f"Step {idx} missing stepType. Provide stepType or shorthand 'type'."
            )
        current["stepType"] = _build_step_type(step_type)

        if "stepOrder" not in current:
            current["stepOrder"] = idx

        current.setdefault("type", "ExecutableStepDTO")

        if "duration" in current:
            duration = current.pop("duration")
            if "endCondition" not in current:
                current["endCondition"] = {"conditionTypeKey": "time"}
            if "endConditionValue" not in current:
                current["endConditionValue"] = duration

        end_condition = current.get("endCondition")
        if isinstance(end_condition, str):
            current["endCondition"] = {"conditionTypeKey": end_condition}
            end_condition = current["endCondition"]
        if isinstance(end_condition, dict):
            current["endCondition"] = _build_end_condition(end_condition)

        target_type = current.get("targetType")
        if target_type is None and "target" in current:
            target_type_key, target_value = _parse_target(current.pop("target"))
            current["targetType"] = {"workoutTargetTypeKey": target_type_key}
            if target_value is not None:
                current["targetValue"] = target_value
        elif isinstance(target_type, str):
            current["targetType"] = {"workoutTargetTypeKey": target_type}

        if "targetType" not in current:
            current["targetType"] = {"workoutTargetTypeKey": "no.target"}

        target_type = current.get("targetType")
        if isinstance(target_type, dict):
            current["targetType"] = _build_target_type(target_type)

        normalized.append(current)
    return normalized


def _load_workout_payload(file_path: str) -> dict[str, Any]:
    try:
        with open(file_path, "r") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise GarminCliError(f"Invalid workout JSON file: {exc}") from exc
    if not isinstance(payload, dict):
        raise GarminCliError("Workout JSON file must contain an object.")
    return payload


def _estimate_duration(steps: list[dict[str, Any]]) -> int:
    total = 0.0
    for step in steps:
        end_condition = step.get("endCondition")
        if not isinstance(end_condition, dict):
            continue
        condition_key = end_condition.get("conditionTypeKey")
        if isinstance(condition_key, str) and condition_key.lower() == "time":
            value = step.get("endConditionValue")
            if isinstance(value, (int, float)):
                total += float(value)
    return int(round(total))


def _build_workout_payload(
    name: Optional[str],
    sport_key: Optional[str],
    sport_id: Optional[int],
    steps: Optional[list[dict[str, Any]]],
) -> dict[str, Any]:
    if not name or not sport_key or sport_id is None or not steps:
        raise GarminCliError(
            "Provide --file or --name, --sport, and --steps "
            "(--sport-id can be inferred from --sport)."
        )

    sport = {"sportTypeKey": sport_key, "sportTypeId": sport_id}
    display_order = SPORT_TYPE_DISPLAY_ORDER.get(sport_key.lower())
    if display_order is not None:
        sport["displayOrder"] = display_order
    return {
        "workoutName": name,
        "estimatedDurationInSecs": _estimate_duration(steps),
        "sportType": sport,
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": sport,
                "workoutSteps": steps,
            }
        ],
    }


def _iter_activity_type_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [entry for entry in data if isinstance(entry, dict)]
    if isinstance(data, dict):
        for key in ("activityTypes", "activityType", "types", "activityTypesV2"):
            value = data.get(key)
            if isinstance(value, list):
                return [entry for entry in value if isinstance(entry, dict)]
    return []


def _extract_type_key_id(entry: dict[str, Any]) -> Tuple[Optional[str], Optional[int]]:
    if "typeKey" in entry and "typeId" in entry:
        return entry.get("typeKey"), entry.get("typeId")
    if "sportTypeKey" in entry and "sportTypeId" in entry:
        return entry.get("sportTypeKey"), entry.get("sportTypeId")
    if "activityType" in entry and isinstance(entry["activityType"], dict):
        return _extract_type_key_id(entry["activityType"])
    if "type" in entry and isinstance(entry["type"], dict):
        return _extract_type_key_id(entry["type"])
    return None, None


def _resolve_sport_type(
    client: Any, sport_key: Optional[str], sport_id: Optional[int]
) -> Tuple[str, int]:
    if sport_key and sport_id is not None:
        return sport_key, sport_id

    entries = _iter_activity_type_entries(api_call(client.get_activity_types))
    mapping: dict[str, Tuple[str, int]] = {}
    for entry in entries:
        key, type_id = _extract_type_key_id(entry)
        if not key or type_id is None:
            continue
        try:
            type_id_int = int(type_id)
        except (TypeError, ValueError):
            continue
        mapping[key.lower()] = (key, type_id_int)

    if sport_key and sport_id is None:
        found = mapping.get(sport_key.lower())
        if not found:
            raise GarminCliError(
                f"Unknown sport '{sport_key}'. "
                "Use 'gc activities types' to list available sports."
            )
        return found

    if sport_key is None and sport_id is not None:
        for key, type_id in mapping.values():
            if type_id == sport_id:
                return key, type_id
        raise GarminCliError(
            f"Unknown sport id '{sport_id}'. "
            "Provide --sport or use 'gc activities types' to list available sports."
        )

    raise GarminCliError("Provide --sport or --sport-id.")


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
        payload = None
        steps_payload = None
        if file:
            payload = _load_workout_payload(file)
        else:
            if steps is None:
                raise GarminCliError("Provide --file or --steps.")
            steps_payload = _normalize_steps(_parse_steps(steps))

        client = load_client(tokenstore=tokenstore)
        if payload is None:
            sport_key, resolved_id = _resolve_sport_type(client, sport, sport_id)
            payload = _build_workout_payload(
                name, sport_key, resolved_id, steps_payload
            )
        if hasattr(client, "upload_workout"):
            data = api_call(client.upload_workout, payload)
        else:
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
        payload = None
        steps_payload = None
        if file:
            payload = _load_workout_payload(file)
        else:
            if steps is None:
                raise GarminCliError("Provide --file or --steps.")
            steps_payload = _normalize_steps(_parse_steps(steps))

        client = load_client(tokenstore=tokenstore)
        if payload is None:
            sport_key, resolved_id = _resolve_sport_type(client, sport, sport_id)
            payload = _build_workout_payload(
                name, sport_key, resolved_id, steps_payload
            )
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
