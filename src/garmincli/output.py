"""Output formatting for JSON and Rich tables."""

import json
from typing import Any, Optional

from rich.console import Console
from rich.table import Table

_CONSOLE_KWARGS = {
    "color_system": None,
    "no_color": True,
    "highlight": False,
    "emoji": False,
    "width": 200,
}

console = Console(**_CONSOLE_KWARGS)
err_console = Console(stderr=True, **_CONSOLE_KWARGS)


def print_json(data: Any, output: Optional[str] = None) -> None:
    """Print data as formatted JSON."""
    text = json.dumps(data, default=str, indent=2)
    if output:
        with open(output, "w") as f:
            f.write(text)
    else:
        console.print(text)


def print_table(
    data: Any,
    columns: Optional[list[str]] = None,
    title: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """Print data as a Rich table."""
    if data is None:
        err_console.print("[yellow]No data available.[/yellow]")
        return

    if isinstance(data, dict) and not columns:
        _print_dict_table(data, title=title, output=output)
        return

    if isinstance(data, list):
        if not data:
            err_console.print("[yellow]No data available.[/yellow]")
            return
        if isinstance(data[0], dict):
            _print_list_table(data, columns=columns, title=title, output=output)
            return

    # Fallback: print as JSON
    print_json(data, output=output)


def _print_dict_table(
    data: dict, title: Optional[str] = None, output: Optional[str] = None
) -> None:
    """Print a dict as a two-column key-value table."""
    table = _new_table(title=title, show_header=True)
    table.add_column("Field", no_wrap=True)
    table.add_column("Value")
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        table.add_row(str(key), str(value) if value is not None else "-")
    _output_table(table, output)


def _print_list_table(
    data: list[dict],
    columns: Optional[list[str]] = None,
    title: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """Print a list of dicts as a table."""
    if not columns:
        columns = list(data[0].keys())

    table = _new_table(title=title, show_header=True)
    for col in columns:
        table.add_column(col, no_wrap=False)

    for row in data:
        values = []
        for col in columns:
            val = row.get(col)
            if isinstance(val, (dict, list)):
                val = json.dumps(val, default=str)
            values.append(str(val) if val is not None else "-")
        table.add_row(*values)

    _output_table(table, output)


def _output_table(table: Table, output: Optional[str] = None) -> None:
    """Output table to console or file."""
    if output:
        with open(output, "w") as f:
            file_console = Console(file=f, **_CONSOLE_KWARGS)
            file_console.print(table)
    else:
        console.print(table)


def _new_table(title: Optional[str], show_header: bool) -> Table:
    return Table(
        title=title,
        show_header=show_header,
        box=None,
        show_edge=False,
        pad_edge=False,
        collapse_padding=True,
        expand=False,
    )


def render(
    data: Any,
    fmt: str = "table",
    columns: Optional[list[str]] = None,
    title: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """Render data in the specified format."""
    if fmt == "json":
        print_json(data, output=output)
    else:
        print_table(data, columns=columns, title=title, output=output)


def print_error(message: str) -> None:
    """Print an error message."""
    err_console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    err_console.print(f"[green]{message}[/green]")
