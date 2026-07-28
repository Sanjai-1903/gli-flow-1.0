import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MANIFEST = (
    BASE_DIR
    / "environment"
    / "manifests"
    / "base_environment.json"
)

FINGERPRINT = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "environment_fingerprint.json"
)

with open(MANIFEST) as f:
    manifest = json.load(f)

with open(FINGERPRINT) as f:
    fingerprint = json.load(f)

print("=" * 60)
print("GLI-FLOW Environment Consistency Check")
print("=" * 60)
print()

validated = manifest["validated_with"]
toolchain = fingerprint["toolchain"]

consistency_report = []

for tool, expected_version in validated.items():

    detected = toolchain.get(
        tool,
        "UNAVAILABLE"
    )

    status = "MATCH"

    if detected == "UNAVAILABLE":
        status = "MISSING"

    consistency_report.append({

        "tool": tool,
        "expected": expected_version,
        "detected": detected,
        "status": status
    })

    print(f"{tool}")
    print(f"  Expected : {expected_version}")
    print(f"  Detected : {detected}")
    print(f"  Status   : {status}")
    print()

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "environment_consistency_report.json"
)

with open(output, "w") as f:
    json.dump(
        consistency_report,
        f,
        indent=4
    )

print(f"[OUTPUT] {output}")
