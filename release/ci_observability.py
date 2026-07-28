import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

WORKFLOW_DIR = (
    BASE_DIR
    / ".github"
    / "workflows"
)

workflows = []

print("=" * 60)
print("GLI-FLOW CI Observability")
print("=" * 60)
print()

if WORKFLOW_DIR.exists():

    for workflow in WORKFLOW_DIR.glob("*.yml"):

        workflow_info = {

            "workflow_name":
                workflow.name,

            "path":
                str(workflow.resolve())
        }

        workflows.append(workflow_info)

        print(f"{workflow.name}")

report = {

    "generated_at":
        str(datetime.now()),

    "workflow_count":
        len(workflows),

    "workflows":
        workflows
}

output = (
    BASE_DIR
    / "outputs"
    / "reports"
    / "ci_observability_report.json"
)

with open(output, "w") as f:
    json.dump(
        report,
        f,
        indent=4
    )

print()
print("=" * 60)
print(f"[OUTPUT] {output}")
