import pytest

from garmincli.commands.workouts import _normalize_steps, _parse_steps
from garmincli.errors import GarminCliError


def test_parse_steps_simple() -> None:
    raw = '[{"stepType":{"stepTypeKey":"warmup"}},{"stepType":{"stepTypeKey":"cooldown"}}]'
    steps = _parse_steps(raw)
    assert steps == [
        {"stepType": {"stepTypeKey": "warmup"}},
        {"stepType": {"stepTypeKey": "cooldown"}},
    ]


def test_parse_steps_full_schema() -> None:
    steps = _parse_steps(
        '[{"stepType":{"stepTypeKey":"warmup"},'
        '"endCondition":{"conditionTypeKey":"time"},'
        '"endConditionValue":300}]'
    )
    assert steps[0]["stepType"]["stepTypeKey"] == "warmup"


def test_parse_steps_invalid_json() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps("not-json")


def test_parse_steps_invalid_root_type() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps('{"stepType":{"stepTypeKey":"warmup"}}')


def test_parse_steps_invalid_entry() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps('[1]')


def test_normalize_steps_shorthand_duration() -> None:
    steps = _normalize_steps(
        _parse_steps(
            '[{"type":"warmup","duration":600},{"type":"interval","duration":1200}]'
        )
    )
    assert steps[0]["stepOrder"] == 1
    assert steps[0]["stepType"]["stepTypeKey"] == "warmup"
    assert steps[0]["endCondition"]["conditionTypeKey"] == "time"
    assert steps[0]["endConditionValue"] == 600
    assert steps[0]["targetType"]["workoutTargetTypeKey"] == "no.target"


def test_normalize_steps_target_hr_zone() -> None:
    steps = _normalize_steps(
        _parse_steps('[{"type":"interval","duration":300,"target":"hr_zone:2"}]')
    )
    assert steps[0]["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
    assert steps[0]["targetValue"] == 2
