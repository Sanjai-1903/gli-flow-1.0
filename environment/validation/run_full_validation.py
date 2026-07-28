import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

validation_steps = [

    {
        "name": "Environment Validation",
        "script": "validate_environment.py"
    },

    {
        "name": "Remediation Guidance",
        "script": "remediation_engine.py"
    },

    {
        "name": "Environment Fingerprint",
        "script": "environment_fingerprint.py"
    },

    {
        "name": "Consistency Check",
        "script": "check_environment_consistency.py"
    }
]

print("=" * 60)
print("GLI-FLOW Full Validation Pipeline")
print("=" * 60)
print()

for step in validation_steps:

    print(f"[RUNNING] {step['name']}")
    print("-" * 60)

    script_path = (
        BASE_DIR
        / "environment"
        / "validation"
        / step["script"]
    )

    subprocess.run([
        "python3",
        str(script_path)
    ])

    print()

print("=" * 60)
print("Validation Pipeline Complete")
print("=" * 60)
