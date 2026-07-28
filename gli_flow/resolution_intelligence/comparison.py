"""Run comparison engine — compares failed and successful runs.

Helps identify why recovery succeeded by showing:
- Config changes
- Parameter changes
- QoR changes
- Failure differences
"""

import json
from typing import Optional

from gli_flow.resolution_intelligence.models import RunComparison


COMPARABLE_FIELDS = [
    "wns", "tns", "hold_wns", "hold_tns",
    "utilization", "runtime_sec", "cell_count",
    "qor_score", "drc_violations",
    "setup_wns_ns", "hold_whs_ns",
]


class RunComparisonEngine:

    def compare(self, run_a: dict, run_b: dict) -> RunComparison:
        """Compare two runs and identify changes."""
        comparison = RunComparison(
            run_id_a=run_a.get("run_id", ""),
            run_id_b=run_b.get("run_id", ""),
        )

        for field in COMPARABLE_FIELDS:
            val_a = run_a.get(field)
            val_b = run_b.get(field)
            if val_a is not None and val_b is not None:
                try:
                    delta = float(val_b) - float(val_a)
                except (ValueError, TypeError):
                    delta = None
                comparison.fields[field] = {
                    "before": val_a,
                    "after": val_b,
                    "delta": delta,
                }

        comparison.qor_changes = {
            k: v for k, v in comparison.fields.items()
            if k in ("wns", "tns", "qor_score", "utilization", "drc_violations")
        }

        return comparison

    def compare_with_failures(
        self,
        run_a: dict,
        run_b: dict,
        failures_a: list[dict],
        failures_b: list[dict],
    ) -> RunComparison:
        """Compare two runs including their failure sets."""
        comparison = self.compare(run_a, run_b)

        failure_types_a = {f.get("failure_type") for f in failures_a}
        failure_types_b = {f.get("failure_type") for f in failures_b}

        resolved = failure_types_a - failure_types_b
        new_failures = failure_types_b - failure_types_a
        persistent = failure_types_a & failure_types_b

        comparison.failure_diffs = [
            {"type": "resolved", "failures": sorted(resolved)},
            {"type": "new", "failures": sorted(new_failures)},
            {"type": "persistent", "failures": sorted(persistent)},
        ]

        return comparison
