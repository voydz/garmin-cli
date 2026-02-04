"""Date parsing and shortcut handling."""

from datetime import date, timedelta
from typing import Optional

import typer

DATE_FORMAT = "%Y-%m-%d"

SHORTCUTS = {
    "today": lambda: (date.today(), None),
    "yesterday": lambda: (date.today() - timedelta(days=1), None),
    "week": lambda: (date.today() - timedelta(days=7), date.today()),
    "month": lambda: (date.today() - timedelta(days=30), date.today()),
}


def parse_date(value: str) -> date:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        from datetime import datetime

        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        raise typer.BadParameter(f"Invalid date format: {value}. Use YYYY-MM-DD.")


def fmt(d: date) -> str:
    """Format a date as YYYY-MM-DD string."""
    return d.strftime(DATE_FORMAT)


def resolve_date(
    date_shortcut: Optional[str] = None,
    date_str: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """Resolve date arguments into (start_date, end_date) strings.

    Returns a tuple of (start_date_str, end_date_str).
    end_date_str is None for single-date queries.
    """
    if date_shortcut and date_shortcut in SHORTCUTS:
        d, end_d = SHORTCUTS[date_shortcut]()
        return fmt(d), fmt(end_d) if end_d else None

    if date_shortcut:
        d = parse_date(date_shortcut)
        return fmt(d), None

    if start and end:
        return fmt(parse_date(start)), fmt(parse_date(end))

    if date_str:
        return fmt(parse_date(date_str)), None

    return fmt(date.today()), None
