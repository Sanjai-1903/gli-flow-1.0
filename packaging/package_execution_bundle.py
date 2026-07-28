from pathlib import Path
import tarfile
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

FILES_TO_PACKAGE = [

    "openroad_metrics.json",
    "run_scores.json",
    "execution_dataset.json",
    "execution_timeline.json",
    "execution_provenance_graph.json",
    "execution_health_report.json",
    "release_validation_report.json",
    "artifact_manifest.json"
]

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

bundle_name = (
    BASE_DIR
    / "packaging"
    / f"gli_flow_bundle_{timestamp}.tar.gz"
)

with tarfile.open(
    bundle_name,
    "w:gz"
) as tar:

    for file_name in FILES_TO_PACKAGE:

        file_path = BASE_DIR / file_name

        if file_path.exists():

            tar.add(
                file_path,
                arcname=file_name
            )

print("=" * 60)
print("GLI-FLOW Packaging Engine")
print("=" * 60)
print()

print(f"[BUNDLE CREATED]")
print(bundle_name)

print()
print("[INCLUDED FILES]")

for file_name in FILES_TO_PACKAGE:
    print(f" - {file_name}")
