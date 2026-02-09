from datetime import date

import pytest
import typer

from garmincli import dates


class FixedDate(date):
    @classmethod
    def today(cls) -> "FixedDate":
        return cls(2025, 1, 15)


def test_parse_date_valid() -> None:
    assert dates.parse_date("2025-01-03") == date(2025, 1, 3)


def test_parse_date_invalid() -> None:
    with pytest.raises(typer.BadParameter):
        dates.parse_date("2025/01/03")


def test_resolve_date_shortcuts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dates, "date", FixedDate)
    assert dates.resolve_date("today") == ("2025-01-15", None)
    assert dates.resolve_date("yesterday") == ("2025-01-14", None)
    assert dates.resolve_date("week") == ("2025-01-08", "2025-01-15")
    assert dates.resolve_date("month") == ("2024-12-16", "2025-01-15")


def test_resolve_date_range() -> None:
    assert dates.resolve_date(start="2025-02-01", end="2025-02-10") == (
        "2025-02-01",
        "2025-02-10",
    )


def test_resolve_date_single_date() -> None:
    assert dates.resolve_date(date_str="2025-02-05") == ("2025-02-05", None)
