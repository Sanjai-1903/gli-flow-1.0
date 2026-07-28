import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RUNS_DIR = (
    BASE_DIR
    / "openroad_runs"
)

REPORTS_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

runs = sorted(
    [

        r for r in RUNS_DIR.iterdir()
        if r.is_dir()

    ],

    key=lambda x:
    x.stat().st_mtime
)

reports = sorted(
    REPORTS_DIR.glob("*.json"),

    key=lambda x:
    x.stat().st_mtime
)

navigation = {

    "latest_run": None,
    "latest_log": None,
    "latest_report": None
}

if runs:

    latest_run = runs[-1]

    navigation["latest_run"] = str(
        latest_run.resolve()
    )

    log_file = (
        latest_run
        / "openroad.log"
    )

    if log_file.exists():

        navigation["latest_log"] = str(
            log_file.resolve()
        )

if reports:

    latest_report = reports[-1]

    navigation["latest_report"] = str(
        latest_report.resolve()
    )

print("=" * 60)
print("GLI-FLOW Navigation Index")
print("=" * 60)
print()

for key, value in navigation.items():

    print(f"{key}")
    print(f"  {value}")
    print()

output = (
    REPORTS_DIR
    / "navigation_index.json"
)

with open(output, "w") as f:
    json.dump(
        navigation,
        f,
        indent=4
    )

print("=" * 60)
print(f"[OUTPUT] {output}")
