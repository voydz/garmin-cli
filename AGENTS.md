## QA methods (product-level)
- Unit tests for date parsing, workout step parsing, and error handling.
- Contract tests around Garmin API wrapper responses using recorded fixtures/mocked clients.
- CLI smoke tests for key commands (`gc --help`, `gc status`) with isolated tokenstore.
- Always verify changes by running the CLI command(s) that exercise the modified code path(s).
- Verify raw API calls via `gc api` for endpoints touched by changes.
  - Example: `uv run gc api /biometric-service/biometric/latestFunctionalThresholdPower/CYCLING`
- Golden-file output tests for JSON/table rendering to prevent regressions.
- Manual exploratory testing for login/MFA flows and workout write endpoints.

## Required checks (run every time)
- `make lint`
- `make test`

If checks cannot be run, report the reason and provide the exact commands to run.

## Dev usage
- Use the repo version without a build via uv:
  - `uv sync`
  - `uv run gc --help`
  - `uv run python -m garmincli --help`

## Raw API exploration
- The CLI supports direct Garmin Connect API calls once authenticated.
- Example:
  - `uv run gc api /biometric-service/biometric/latestFunctionalThresholdPower/CYCLING`
- Use `--method`, `--params` (JSON object), and `--body` (JSON) for explicit requests.
