---
name: garmin
description: Read health, fitness, and activity data from Garmin Connect via a non-interactive CLI.
metadata: {"clawdbot":{"emoji":"⌚","requires":{"bins":["gc"]}}}
---

# Garmin Connect CLI

This skill provides read access to Garmin Connect health and fitness data through the `gc` CLI.

## Setup

1.  **Install via Homebrew tap:**
    ```bash
    brew tap voydz/homebrew-tap
    brew install garmin-cli
    ```

2.  **Authentication:**
    ```bash
    gc login --email user@example.com --password secret
    # With MFA:
    gc login --email user@example.com --password secret --mfa 123456
    ```

3.  **Verify connection:**
    ```bash
    gc status
    ```

## Date Shortcuts

Most commands accept a date shortcut as first argument:

- `today` — current date
- `yesterday` — previous date
- `week` — last 7 days (returns a date range)
- `month` — last 30 days (returns a date range)
- `YYYY-MM-DD` — specific date

Alternatively use `--date`, `--start`/`--end` flags.

## Output

All data commands support:

- `--format json` for machine-readable output (default: `table`)
- `--output FILE` to write to a file

Always use `--format json` when parsing output programmatically.

## Usage

```bash
# Authentication
gc login --email EMAIL --password PASS [--mfa CODE | --wait-mfa]
gc logout
gc status
gc status --profile

# Daily Health
gc health today
gc steps today
gc steps week
gc steps --weekly --weeks N
gc steps --start DATE --end DATE
gc floors today
gc intensity today
gc intensity --weekly --weeks N
gc events today

# Heart Rate
gc heart today
gc heart resting today

# Sleep
gc sleep today

# Stress & Body Battery
gc stress today
gc stress --weekly --weeks N
gc stress all-day today
gc battery today
gc battery --start DATE --end DATE
gc battery --events today

# Vitals
gc respiration today
gc spo2 today
gc blood-pressure today [--end DATE]
gc lifestyle today

# Hydration
gc hydration today

# Activities
gc activities                                     # List recent (default 20)
gc activities --limit N --offset N --type TYPE
gc activities --start DATE --end DATE [--type TYPE]
gc activities today                               # Activities for a date
gc activities last                                # Most recent activity
gc activities get ID                              # Activity summary by ID
gc activities count                               # Total count
gc activities details ID
gc activities splits ID
gc activities typed-splits ID
gc activities split-summaries ID
gc activities weather ID
gc activities hr-zones ID
gc activities power-zones ID
gc activities exercise-sets ID
gc activities types                               # List all activity types
gc activities gear ID                             # Gear used for activity
gc activities progress --start DATE --end DATE --metric distance|duration|elevation
gc activities download ID --format fit|tcx|gpx|kml|csv [-o FILE]
gc activities upload FILE                         # .fit, .gpx, .tcx

# Body & Weight
gc body today [--end DATE]
gc body weighins today
gc body weighins --start DATE --end DATE

# Advanced Metrics
gc metrics vo2max today
gc metrics hrv today
gc metrics training-readiness today
gc metrics morning-readiness today
gc metrics training-status today
gc metrics fitness-age today
gc metrics race-predictions
gc metrics race-predictions --start DATE --end DATE --type daily|monthly
gc metrics endurance-score today [--end DATE]
gc metrics hill-score today [--end DATE]
gc metrics lactate-threshold                      # Latest
gc metrics lactate-threshold --no-latest --start DATE --end DATE --aggregation daily|weekly|monthly|yearly
gc metrics cycling-ftp

# Devices
gc devices                                        # List all devices
gc devices last-used
gc devices primary
gc devices settings DEVICE_ID
gc devices alarms
gc devices solar DEVICE_ID today [--end DATE]

# Goals, Records, Badges & Challenges
gc records
gc goals [--status active|future|past] [--limit N]
gc badges earned
gc badges available
gc badges in-progress
gc challenges adhoc [--start N --limit N]
gc challenges badge [--start N --limit N]
gc challenges available [--start N --limit N]
gc challenges non-completed [--start N --limit N]
gc challenges virtual [--start N --limit N]

# Gear
gc gear USER_PROFILE_NUMBER                       # List gear (profile number from gc status --profile)
gc gear defaults USER_PROFILE_NUMBER
gc gear stats GEAR_UUID
gc gear activities GEAR_UUID [--limit N]

# Workouts & Training Plans
gc workouts [--start N --limit N]
gc workouts get WORKOUT_ID
gc workouts download WORKOUT_ID [-o FILE]
gc workouts scheduled WORKOUT_ID
gc workouts create --file workout.json
gc workouts create --name "Zone 2 Grundlage" --sport cycling --steps '[{"type":"warmup","duration":600},{"type":"interval","duration":3600,"target":"hr_zone:2"},{"type":"cooldown","duration":300}]'
gc workouts update WORKOUT_ID --file workout.json
gc workouts delete WORKOUT_ID
gc training-plans
gc training-plans get PLAN_ID
gc training-plans adaptive PLAN_ID

# Menstrual Cycle
gc menstrual today
gc menstrual calendar --start DATE --end DATE
gc menstrual pregnancy
```

## Examples

**Get today's health summary as JSON:**
```bash
gc health today --format json
```

**Get last week's steps as JSON for analysis:**
```bash
gc steps week --format json
```

**Find the user's most recent run:**
```bash
gc activities --limit 5 --type running --format json
```

**Get detailed info about a specific activity:**
```bash
gc activities get 12345678 --format json
```

**Download an activity as GPX:**
```bash
gc activities download 12345678 --format gpx -o run.gpx
```

**Check training readiness and HRV:**
```bash
gc metrics training-readiness today --format json
gc metrics hrv today --format json
```

**Get sleep and body battery for yesterday:**
```bash
gc sleep yesterday --format json
gc battery yesterday --format json
```

**List devices and get solar data:**
```bash
gc devices --format json
gc devices solar DEVICE_ID today --format json
```
