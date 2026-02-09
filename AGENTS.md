## QA methods (product-level)
- Unit tests for date parsing, workout step parsing, and error handling.
- Contract tests around Garmin API wrapper responses using recorded fixtures/mocked clients.
- CLI smoke tests for key commands (`gc --help`, `gc status`) with isolated tokenstore.
- Golden-file output tests for JSON/table rendering to prevent regressions.
- Manual exploratory testing for login/MFA flows and workout write endpoints.

## Required checks (run every time)
- `make lint`
- `make test`

If checks cannot be run, report the reason and provide the exact commands to run.
