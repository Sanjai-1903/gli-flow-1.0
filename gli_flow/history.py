import json

from pathlib import Path


RUNS_ROOT = Path(
    "outputs/runs"
)


def get_run_history():

    if not RUNS_ROOT.exists():

        return []

    runs = []

    for run_dir in sorted(
        RUNS_ROOT.iterdir()
    ):

        if not run_dir.is_dir():

            continue

        metadata_file = (
            run_dir
            / "execution_metadata.json"
        )

        if not metadata_file.exists():

            continue

        try:

            with open(metadata_file) as f:

                metadata = json.load(f)

            runs.append(metadata)

        except Exception:

            continue

    return runs
