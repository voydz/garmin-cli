# BUGS.md

## 2026-02-15 — `gc workouts create` fails with HTTP 500 (Garmin Connect workout-service)

### Summary
Attempting to create a cycling workout in Garmin Connect via the `gc` CLI fails consistently with `500 Server Error: Internal Server Error` for the endpoint:

- `POST https://connectapi.garmin.com/workout-service/workout`

Read-only endpoints (activities, sleep, battery, profile) work, but workout creation/listing does not.

### Environment
- Host OS: macOS (Darwin arm64)
- Tool: `gc` (garmin-cli) using `garth`/`requests` under the hood
- User context: Felix (Garmin Connect userId 142446077)

### Commands executed
All of these failed with the same HTTP 500:

```bash
gc workouts create --name "Base Z2 60 (10/40/10)" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":2400,"target":"hr_zone:2"},{"type":"cooldown","duration":600}]'

gc workouts create --name "Base Z2 75 (10/55/10)" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":3300,"target":"hr_zone:2"},{"type":"cooldown","duration":600}]'

gc workouts create --name "Base Z2 90 (10/70/10)" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":4200,"target":"hr_zone:2"},{"type":"cooldown","duration":600}]'

# Minimal payload (no target) also fails:
gc workouts create --name "Base Ride 60" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":2400},{"type":"cooldown","duration":600}]'
```

Related observation:

```bash
gc workouts --start 1 --limit 5 --format json
# => []
```

### Full error (representative)

```text
Traceback (most recent call last):
  File "garth/http.py", line 146, in request
  File "requests/models.py", line 1026, in raise_for_status
requests.exceptions.HTTPError: 500 Server Error: Internal Server Error for url: https://connectapi.garmin.com/workout-service/workout

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "__main__.py", line 6, in <module>
  File "typer/main.py", line 336, in __call__
  File "typer/main.py", line 319, in __call__
  File "click/core.py", line 1485, in __call__
  File "typer/core.py", line 814, in main
  File "typer/core.py", line 190, in _main
  File "click/core.py", line 1873, in invoke
  File "click/core.py", line 1873, in invoke
  File "click/core.py", line 1269, in invoke
  File "click/core.py", line 824, in invoke
  File "typer/main.py", line 706, in wrapper
  File "garmincli/commands/workouts.py", line 361, in create
    data = _workout_request(client, "POST", "/workout-service/workout", payload)
  File "garmincli/commands/workouts.py", line 244, in _workout_request
    return _call_connectapi(garth.connectapi, path, method, payload)
  File "garmincli/commands/workouts.py", line 220, in _call_connectapi
    return connectapi(path, **kwargs)
  File "garth/http.py", line 189, in connectapi
  File "garth/http.py", line 148, in request
garth.exc.GarthHTTPError: Error in request: 500 Server Error: Internal Server Error for url: https://connectapi.garmin.com/workout-service/workout
[PYI-64399:ERROR] Failed to execute script '__main__' due to unhandled exception!

Command exited with code 1
```

### Notes / Hypotheses
- Likely Garmin backend issue or payload schema mismatch (server returning 500 instead of 4xx).
- Could be an auth/scopes issue specific to workout-service while other services work.
- Could be a regression in Garmin Connect API behavior affecting `garth`/garmin-cli.

### Suggested next steps
1. Retry later to rule out transient Garmin service outage.
2. Inspect the exact JSON payload that `gc` sends (add debug logging in `garmincli/commands/workouts.py`).
3. Compare against a known-good workout payload captured from Garmin Connect Web.
4. Confirm whether workout listing should be empty; validate with Garmin Connect UI.

### Fix (2026-02-15)
- Normalize shorthand steps (`type`, `duration`, `target`) into Garmin `workoutSteps` fields
  and default missing `stepOrder`/`targetType` to avoid malformed payloads.
- Allow `--sport-id` to be inferred from `--sport` via activity types lookup.
