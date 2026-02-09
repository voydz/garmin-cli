# Garmin CLI (`gc`)

[![Release](https://img.shields.io/github/v/release/voydz/garmin-cli)](https://github.com/voydz/garmin-cli/releases)
[![Homebrew Tap](https://img.shields.io/badge/homebrew-voydz%2Fhomebrew--tap-blue?logo=homebrew)](https://github.com/voydz/homebrew-tap)

A fully non-interactive CLI to read health data from Garmin Connect.

## Installation

```bash
brew install voydz/tap/garmin-cli
```

Or install from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/voydz/garmin-cli.git
cd garmin-cli
uv sync
uv run gc --help
```

## Authentication

```bash
# Login with email and password
gc login --email you@example.com --password yourpass

# Login with MFA code
gc login --email you@example.com --password yourpass --mfa 123456

# Login waiting for MFA prompt on stdin
gc login --email you@example.com --password yourpass --wait-mfa

# Credentials can also be set via environment variables
export GARMIN_EMAIL="you@example.com"
export GARMIN_PASSWORD="yourpass"
gc login

# Check login status
gc status
gc status --profile

# Logout
gc logout
```

Tokens are stored in `~/.garmin-cli/tokens/` by default. Override with `--tokenstore PATH` or the `GARMINTOKENS` environment variable.

## Usage

Most commands accept a date shortcut as their first argument:

| Shortcut | Meaning |
|------------|----------------------|
| `today` | Today's date |
| `yesterday` | Yesterday's date |
| `week` | Last 7 days |
| `month` | Last 30 days |
| `YYYY-MM-DD` | Specific date |

### Global Options

All data commands support:

- `--format json` or `--format table` (default: `table`)
- `--output FILE` to write output to a file
- `--tokenstore PATH` to use a custom token directory

### Daily Health

```bash
gc health today
gc health yesterday --format json
gc steps week
gc steps --weekly --weeks 8
gc steps --start 2025-01-01 --end 2025-01-31
gc floors today
gc intensity today
gc intensity --weekly
gc events yesterday
```

### Heart Rate

```bash
gc heart today
gc heart resting yesterday
```

### Sleep

```bash
gc sleep today
```

### Stress & Body Battery

```bash
gc stress today
gc stress --weekly --weeks 4
gc stress all-day yesterday

gc battery today
gc battery --start 2025-01-01 --end 2025-01-07
gc battery --events today
```

### Vitals

```bash
gc respiration today
gc spo2 today
gc blood-pressure today
gc blood-pressure --end 2025-01-31
gc lifestyle today
```

### Activities

```bash
gc activities                              # List recent activities
gc activities --limit 50 --type running
gc activities --start 2025-01-01 --end 2025-01-31
gc activities today
gc activities last
gc activities get 12345678
gc activities count
gc activities details 12345678
gc activities splits 12345678
gc activities typed-splits 12345678
gc activities split-summaries 12345678
gc activities weather 12345678
gc activities hr-zones 12345678
gc activities power-zones 12345678
gc activities exercise-sets 12345678
gc activities types
gc activities gear 12345678
gc activities progress --start 2025-01-01 --end 2025-12-31 --metric distance

# Download and upload
gc activities download 12345678 --format fit -o myrun.zip
gc activities download 12345678 --format gpx
gc activities upload myactivity.fit
```

### Body & Weight

```bash
gc body today
gc body --end 2025-01-31
gc body weighins today
gc body weighins --start 2025-01-01 --end 2025-01-31
```

### Advanced Metrics

```bash
gc metrics vo2max today
gc metrics hrv today
gc metrics training-readiness today
gc metrics morning-readiness today
gc metrics training-status today
gc metrics fitness-age today
gc metrics race-predictions
gc metrics race-predictions --start 2025-01-01 --end 2025-06-01 --type monthly
gc metrics endurance-score today
gc metrics endurance-score --end 2025-01-31
gc metrics hill-score today
gc metrics lactate-threshold
gc metrics lactate-threshold --no-latest --start 2025-01-01 --end 2025-06-01
gc metrics cycling-ftp
```

### Hydration

```bash
gc hydration today
```

### Devices

```bash
gc devices
gc devices last-used
gc devices primary
gc devices settings DEVICE_ID
gc devices alarms
gc devices solar DEVICE_ID today
```

### Goals, Badges & Challenges

```bash
gc records
gc goals
gc goals --status past --limit 50
gc badges earned
gc badges available
gc badges in-progress
gc challenges adhoc
gc challenges badge
gc challenges available
gc challenges non-completed
gc challenges virtual
```

### Gear

```bash
gc gear USER_PROFILE_NUMBER
gc gear defaults USER_PROFILE_NUMBER
gc gear stats GEAR_UUID
gc gear activities GEAR_UUID --limit 50
```

### Workouts & Training Plans

```bash
gc workouts
gc workouts get WORKOUT_ID
gc workouts download WORKOUT_ID -o workout.fit
gc workouts scheduled WORKOUT_ID
gc workouts create --file workout.json
gc workouts create --name "Zone 2 Grundlage" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":3600,"target":"hr_zone:2"},{"type":"cooldown","duration":300}]'
gc workouts update WORKOUT_ID --file workout.json
gc workouts delete WORKOUT_ID

gc training-plans
gc training-plans get PLAN_ID
gc training-plans adaptive PLAN_ID
```

### Menstrual Cycle

```bash
gc menstrual today
gc menstrual calendar --start 2025-01-01 --end 2025-03-01
gc menstrual pregnancy
```

## Building from Source

Build a standalone macOS ARM64 binary:

```bash
make package
```

The binary will be at `dist/gc`.

## License

MIT
