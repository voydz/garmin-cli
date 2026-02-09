import pytest

from garmincli.commands.workouts import _parse_steps
from garmincli.errors import GarminCliError


def test_parse_steps_simple() -> None:
    steps = _parse_steps(
        '[{"type":"warmup","duration":600},'
        '{"type":"interval","duration":3600,"target":"hr_zone:2"},'
        '{"type":"cooldown","duration":300}]'
    )
    assert len(steps) == 3
    assert steps[0]["stepType"]["stepTypeKey"] == "warmup"
    assert steps[1]["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
    assert steps[1]["zoneNumber"] == 2


def test_parse_steps_full_schema() -> None:
    steps = _parse_steps(
        '[{"stepType":{"stepTypeKey":"warmup"},'
        '"endCondition":{"conditionTypeKey":"time"},'
        '"endConditionValue":300}]'
    )
    assert steps[0]["stepOrder"] == 1
    assert steps[0]["stepType"]["stepTypeKey"] == "warmup"


def test_parse_steps_invalid_json() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps("not-json")


def test_parse_steps_invalid_duration() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps('[{"type":"warmup","duration":"oops"}]')


def test_parse_steps_invalid_target() -> None:
    with pytest.raises(GarminCliError):
        _parse_steps('[{"type":"warmup","duration":60,"target":"hr_zone:abc"}]')
