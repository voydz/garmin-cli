"""Raw Garmin Connect API calls."""

import json
from typing import Any, Optional

import typer

from ..api import api_call
from ..auth import load_client
from ..errors import GarminCliError
from ..output import print_error, render

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)


def _parse_json(value: Optional[str], label: str, require_object: bool) -> Any:
    if value is None:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise GarminCliError(f"Invalid {label} JSON: {exc}") from exc
    if require_object and not isinstance(parsed, dict):
        raise GarminCliError(f"{label} must be a JSON object.")
    return parsed


@app.callback(invoke_without_command=True)
def connectapi(
    ctx: typer.Context,
    path: Optional[str] = typer.Argument(
        None, help="Connect API path (e.g. /biometric-service/biometric/...)."
    ),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method."),
    params: Optional[str] = typer.Option(
        None, "--params", help="Query params as JSON object."
    ),
    body: Optional[str] = typer.Option(None, "--body", help="Request body as JSON."),
    tokenstore: Optional[str] = typer.Option(
        None, "--tokenstore", help="Token storage path."
    ),
    fmt: str = typer.Option(
        "json", "--format", "-f", help="Output format (json/table)."
    ),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file."),
) -> None:
    """Call Garmin Connect API with explicit path and payload."""
    if ctx.invoked_subcommand is not None:
        return
    if not path:
        print_error("Path is required. Example: /biometric-service/biometric/...")
        raise typer.Exit(1)

    method = method.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        print_error(f"Unsupported method: {method}")
        raise typer.Exit(1)

    try:
        client = load_client(tokenstore=tokenstore)
        query_params = _parse_json(params, "params", require_object=True)
        payload = _parse_json(body, "body", require_object=False)
        data = api_call(
            client.garth.connectapi,
            path,
            method=method,
            params=query_params,
            json=payload,
        )
        render(data, fmt=fmt, title=f"{method} {path}", output=output)
    except GarminCliError as e:
        print_error(str(e))
        raise typer.Exit(1)
