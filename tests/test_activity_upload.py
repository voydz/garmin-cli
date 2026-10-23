import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from click import unstyle
from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.file_id_message import FileIdMessage
from requests import Response
from typer.testing import CliRunner

from garmincli.cli import app
from garmincli.commands import activities
from garmincli.errors import ConnectionError
from fit_fixtures import activity_bytes

runner = CliRunner()


@pytest.fixture
def client(monkeypatch):
    client = Mock()
    monkeypatch.setattr(activities, "load_client", lambda tokenstore=None: client)
    return client


@pytest.mark.parametrize("extension", ["fit", "gpx", "tcx"])
def test_no_flag_bypasses_preparation(tmp_path, client, monkeypatch, extension):
    source = tmp_path / f"original.{extension}"
    source.write_bytes(b"unchanged: no parsing, even for this synthetic content")
    client.upload_activity.return_value = {"activityId": 123}
    result = runner.invoke(
        app, ["activities", "upload", str(source), "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    client.upload_activity.assert_called_once_with(str(source))
    assert json.loads(result.stdout) == {"activityId": 123}
    assert f"Uploaded {source}" in result.stderr


@pytest.mark.parametrize(
    "model,product", [("edge-530", 3121), ("edge-840", 4062), ("forerunner-955", 4024)]
)
@pytest.mark.parametrize("response_type", ["dict", "202"])
def test_prepared_copy_exists_during_upload_only(
    tmp_path, client, model, product, response_type
):
    source = tmp_path / "source.fit"
    original = activity_bytes(developer=True)
    source.write_bytes(original)
    paths = []
    response = {"activityId": 123}
    if response_type == "202":
        response = Response()
        response.status_code = 202

    def upload(path):
        path = Path(path)
        assert path != source and path.exists()
        paths.append(path)
        fit = FitFile.from_file(str(path))
        identity = next(
            r.message for r in fit.records if isinstance(r.message, FileIdMessage)
        )
        assert identity.manufacturer == 1 and identity.product == product
        return response

    client.upload_activity.side_effect = upload
    result = runner.invoke(
        app,
        ["activities", "upload", str(source), "--as-device", model, "--format", "json"],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == (
        {"activityId": 123} if response_type == "dict" else "<Response [202]>"
    )
    assert model in result.stderr
    assert f"Uploaded {source}" in result.stderr
    assert len(paths) == 1 and not paths[0].parent.exists()
    assert source.read_bytes() == original


@pytest.mark.parametrize(
    "error", [ConnectionError("synthetic network failure"), KeyboardInterrupt()]
)
def test_upload_error_cleans_copy(tmp_path, client, error):
    source = tmp_path / "source.fit"
    source.write_bytes(activity_bytes())
    paths = []

    def upload(path):
        paths.append(Path(path))
        raise error

    client.upload_activity.side_effect = upload
    result = runner.invoke(
        app, ["activities", "upload", str(source), "--as-device", "edge-530"]
    )
    assert result.exit_code != 0
    assert paths and not paths[0].parent.exists()
    assert "Uploaded" not in result.stderr


@pytest.mark.parametrize(
    "model,data",
    [
        ("edge-999", b"bad"),
        ("edge-530", b"<gpx/>"),
        ("edge-840", activity_bytes()[:-4]),
    ],
)
def test_invalid_selection_or_file_never_loads_account_or_uploads(
    tmp_path, monkeypatch, model, data
):
    source = tmp_path / "invalid.fit"
    source.write_bytes(data)
    load = Mock(side_effect=AssertionError("must not load credentials"))
    monkeypatch.setattr(activities, "load_client", load)
    result = runner.invoke(
        app, ["activities", "upload", str(source), "--as-device", model]
    )
    assert result.exit_code != 0
    assert "FIT" in result.output or "Invalid value" in result.output
    load.assert_not_called()


def test_help_lists_exact_choices():
    result = runner.invoke(app, ["activities", "upload", "--help"], color=False)
    assert result.exit_code == 0
    text = unstyle(result.stdout)
    assert "--as-device" in text
    for model in ("edge-530", "edge-840", "forerunner-955"):
        assert model in text


@pytest.mark.parametrize("fmt,extension", [("json", "json"), ("table", "txt")])
def test_upload_rendering_matches_golden(client, fmt, extension):
    client.upload_activity.return_value = {"activityId": 123}
    result = runner.invoke(
        app, ["activities", "upload", "synthetic.fit", "--format", fmt]
    )
    assert result.exit_code == 0, result.output
    actual = "\n".join(line.rstrip() for line in result.stdout.splitlines()) + "\n"
    expected = (Path(__file__).parent / "golden" / f"upload.{extension}").read_text()
    assert actual == expected
