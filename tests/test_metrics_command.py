from typing import Any

from typer.testing import CliRunner

from garmincli.cli import app
from garmincli.commands import metrics
from garmincli.errors import GarminCliError


runner = CliRunner()


class _DummyClient:
    def get_max_metrics(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_max_metrics", "date": cdate}

    def get_hrv_data(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_hrv_data", "date": cdate}

    def get_training_readiness(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_training_readiness", "date": cdate}

    def get_morning_training_readiness(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_morning_training_readiness", "date": cdate}

    def get_training_status(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_training_status", "date": cdate}

    def get_fitnessage_data(self, cdate: str) -> dict[str, str]:
        return {"endpoint": "get_fitnessage_data", "date": cdate}

    def get_race_predictions(self) -> list[dict[str, str]]:
        return [
            {"endpoint": "get_race_predictions", "snapshot": "older"},
            {"endpoint": "get_race_predictions", "snapshot": "latest"},
        ]

    def get_endurance_score(self, cdate: str, end: str | None) -> dict[str, Any]:
        return {"endpoint": "get_endurance_score", "date": cdate, "end": end}

    def get_hill_score(self, cdate: str, end: str | None) -> dict[str, Any]:
        return {"endpoint": "get_hill_score", "date": cdate, "end": end}

    def get_lactate_threshold(self, latest: bool = True) -> dict[str, bool]:
        return {"endpoint": "get_lactate_threshold", "latest": latest}

    def get_cycling_ftp(self) -> dict[str, str]:
        return {"endpoint": "get_cycling_ftp"}


def _fake_resolve_date(*args: Any, **kwargs: Any) -> tuple[str, None]:
    return ("2025-01-15", None)


def test_metrics_default_aggregates_all_endpoints(
    monkeypatch,
) -> None:
    monkeypatch.setattr(metrics, "load_client", lambda tokenstore=None: _DummyClient())
    monkeypatch.setattr(metrics, "resolve_date", _fake_resolve_date)
    monkeypatch.setattr(metrics, "api_call", lambda func, *args, **kwargs: func(*args, **kwargs))

    captured: dict[str, Any] = {}

    def _capture_render(data: Any, fmt: str, title: str, output: str | None) -> None:
        captured["data"] = data
        captured["fmt"] = fmt
        captured["title"] = title
        captured["output"] = output

    monkeypatch.setattr(metrics, "render", _capture_render)

    result = runner.invoke(app, ["metrics", "--date", "today"])

    assert result.exit_code == 0
    assert captured["fmt"] == "table"
    assert captured["title"] == "Metrics (2025-01-15)"
    assert captured["data"]["vo2max"]["endpoint"] == "get_max_metrics"
    assert captured["data"]["training_status"]["endpoint"] == "get_training_status"
    assert captured["data"]["race_predictions"]["snapshot"] == "latest"
    assert captured["data"]["cycling_ftp"]["endpoint"] == "get_cycling_ftp"


def test_metrics_default_without_args_runs_summary(
    monkeypatch,
) -> None:
    monkeypatch.setattr(metrics, "load_client", lambda tokenstore=None: _DummyClient())
    monkeypatch.setattr(metrics, "resolve_date", _fake_resolve_date)
    monkeypatch.setattr(metrics, "api_call", lambda func, *args, **kwargs: func(*args, **kwargs))

    captured: dict[str, Any] = {}

    def _capture_render(data: Any, fmt: str, title: str, output: str | None) -> None:
        captured["data"] = data
        captured["fmt"] = fmt
        captured["title"] = title
        captured["output"] = output

    monkeypatch.setattr(metrics, "render", _capture_render)

    result = runner.invoke(app, ["metrics"])

    assert result.exit_code == 0
    assert captured["fmt"] == "table"
    assert captured["title"] == "Metrics (2025-01-15)"
    assert captured["data"]["vo2max"]["endpoint"] == "get_max_metrics"


def test_metrics_default_keeps_running_when_single_endpoint_fails(
    monkeypatch,
) -> None:
    monkeypatch.setattr(metrics, "load_client", lambda tokenstore=None: _DummyClient())
    monkeypatch.setattr(metrics, "resolve_date", _fake_resolve_date)

    def _fake_api_call(func, *args, **kwargs):  # noqa: ANN001
        if func.__name__ == "get_training_status":
            raise GarminCliError("training status unavailable")
        return func(*args, **kwargs)

    monkeypatch.setattr(metrics, "api_call", _fake_api_call)

    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        metrics,
        "render",
        lambda data, fmt, title, output: captured.update(  # noqa: ARG005
            {"data": data, "title": title}
        ),
    )

    result = runner.invoke(app, ["metrics", "--date", "today"])

    assert result.exit_code == 0
    assert captured["title"] == "Metrics (2025-01-15)"
    assert captured["data"]["training_status"]["error"] == "training status unavailable"
    assert captured["data"]["vo2max"]["endpoint"] == "get_max_metrics"


def test_metrics_default_uses_training_status_vo2max_fallback_when_daily_is_empty(
    monkeypatch,
) -> None:
    class _Vo2FallbackClient(_DummyClient):
        def get_max_metrics(self, cdate: str) -> list[dict[str, str]]:  # noqa: ARG002
            return []

        def get_training_status(self, cdate: str) -> dict[str, Any]:  # noqa: ARG002
            return {
                "mostRecentVO2Max": {
                    "generic": {
                        "calendarDate": "2025-01-14",
                        "vo2MaxValue": 51.0,
                    }
                }
            }

    monkeypatch.setattr(
        metrics, "load_client", lambda tokenstore=None: _Vo2FallbackClient()
    )
    monkeypatch.setattr(metrics, "resolve_date", _fake_resolve_date)
    monkeypatch.setattr(metrics, "api_call", lambda func, *args, **kwargs: func(*args, **kwargs))

    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        metrics,
        "render",
        lambda data, fmt, title, output: captured.update(  # noqa: ARG005
            {"data": data, "title": title}
        ),
    )

    result = runner.invoke(app, ["metrics", "--date", "today"])

    assert result.exit_code == 0
    assert captured["title"] == "Metrics (2025-01-15)"
    assert captured["data"]["vo2max"]["generic"]["vo2MaxValue"] == 51.0


def test_metrics_subcommand_still_works(
    monkeypatch,
) -> None:
    monkeypatch.setattr(metrics, "load_client", lambda tokenstore=None: _DummyClient())
    monkeypatch.setattr(metrics, "resolve_date", _fake_resolve_date)
    monkeypatch.setattr(metrics, "api_call", lambda func, *args, **kwargs: func(*args, **kwargs))

    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        metrics,
        "render",
        lambda data, fmt, title, output: captured.update(  # noqa: ARG005
            {"data": data, "title": title}
        ),
    )

    result = runner.invoke(app, ["metrics", "vo2max", "today"])

    assert result.exit_code == 0
    assert captured["title"] == "VO2 Max (2025-01-15)"
    assert captured["data"]["endpoint"] == "get_max_metrics"
