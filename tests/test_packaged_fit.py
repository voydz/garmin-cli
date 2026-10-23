"""Run with GC_BINARY=/absolute/path/to/gc, or via make smoke. No account access."""

import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from fit_fixtures import activity_bytes

BINARY = os.environ.get("GC_BINARY")
pytestmark = pytest.mark.skipif(
    not BINARY, reason="standalone binary check: make smoke"
)


def invoke(tmp_path, *args):
    return subprocess.run(
        [str(Path(BINARY).resolve()), *args],
        env={
            "PATH": os.defpath,
            "HOME": str(tmp_path),
            "TMPDIR": str(tmp_path),
            "PYTHONNOUSERSITE": "1",
        },
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_packaged_upload_help(tmp_path):
    result = invoke(tmp_path, "activities", "upload", "--help")
    assert result.returncode == 0, result.stderr
    for text in ("--as-device", "edge-530", "edge-840", "forerunner-955"):
        assert text in result.stdout


@pytest.mark.parametrize("model", ["edge-530", "edge-840", "forerunner-955"])
def test_packaged_transform_stops_at_isolated_auth_boundary(tmp_path, model):
    source = tmp_path / "synthetic.fit"
    source.write_bytes(activity_bytes(developer=True))
    digest = hashlib.sha256(source.read_bytes()).digest()
    result = invoke(
        tmp_path,
        "activities",
        "upload",
        str(source),
        "--as-device",
        model,
        "--tokenstore",
        str(tmp_path / "nonexistent-tokens"),
        "--format",
        "json",
    )
    # The diagnostic occurs after successful decode/edit/rebuild/verification.
    # A nonexistent, explicit tokenstore then stops execution before any API call.
    assert result.returncode == 1, result.stderr
    assert f"({model})" in result.stderr
    assert "Not logged in" in result.stderr
    assert not result.stdout
    assert not list(tmp_path.glob("gc-fit-*"))
    assert hashlib.sha256(source.read_bytes()).digest() == digest
