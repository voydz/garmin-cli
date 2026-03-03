import pytest

from garmincli.commands import workouts
from garmincli.errors import GarminCliError


def _base_payload() -> dict:
    return {
        "workoutId": "111",
        "workoutName": "Old",
        "sportType": {"sportTypeKey": "cycling", "sportTypeId": 2},
        "ownerId": 123,
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": {"sportTypeKey": "cycling", "sportTypeId": 2},
                "workoutSteps": [
                    {
                        "stepOrder": 1,
                        "stepType": {"stepTypeKey": "warmup"},
                    }
                ],
            }
        ],
        "estimatedDurationInSecs": 60,
    }


def test_merge_workout_payload_updates_steps_and_name() -> None:
    base = _base_payload()
    steps = workouts._normalize_steps([
        {"type": "interval", "duration": 300, "target": "power_zone:3"}
    ])

    payload = workouts._merge_workout_payload(
        object(),
        base,
        "222",
        name="New Name",
        sport_key=None,
        sport_id=None,
        steps=steps,
    )

    assert payload["workoutId"] == "222"
    assert payload["workoutName"] == "New Name"
    assert payload["ownerId"] == 123
    assert payload["estimatedDurationInSecs"] == 300
    assert payload["workoutSegments"][0]["workoutSteps"] == steps
    assert payload["workoutSegments"][0]["sportType"]["sportTypeKey"] == "cycling"


def test_merge_workout_payload_updates_sport() -> None:
    base = _base_payload()
    steps = workouts._normalize_steps([
        {"type": "warmup", "duration": 120}
    ])

    def _fake_resolve(client, sport_key, sport_id):
        return "running", 1

    original = workouts._resolve_sport_type
    workouts._resolve_sport_type = _fake_resolve
    try:
        payload = workouts._merge_workout_payload(
            object(),
            base,
            "111",
            name=None,
            sport_key="running",
            sport_id=None,
            steps=steps,
        )
    finally:
        workouts._resolve_sport_type = original

    assert payload["sportType"]["sportTypeKey"] == "running"
    assert payload["sportType"]["sportTypeId"] == 1
    assert payload["sportType"]["displayOrder"] == workouts.SPORT_TYPE_DISPLAY_ORDER[
        "running"
    ]
    assert payload["workoutSegments"][0]["sportType"]["sportTypeKey"] == "running"


def test_merge_workout_payload_rejects_multi_segment() -> None:
    base = _base_payload()
    base["workoutSegments"].append({"segmentOrder": 2, "workoutSteps": []})
    steps = workouts._normalize_steps([
        {"type": "warmup", "duration": 120}
    ])

    with pytest.raises(GarminCliError):
        workouts._merge_workout_payload(
            object(),
            base,
            "111",
            name=None,
            sport_key=None,
            sport_id=None,
            steps=steps,
        )
