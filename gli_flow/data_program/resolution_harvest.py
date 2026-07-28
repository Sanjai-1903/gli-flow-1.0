import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from gli_flow.database.migrations import _get_db_path

log = logging.getLogger(__name__)

PARAM_CHANGE_CANDIDATES = [
    "clock_period_ns",
    "utilization",
    "setup_wns_ns",
    "setup_tns_ns",
    "hold_whs_ns",
    "hold_ths_ns",
    "drc_total_violations",
    "overflow_h",
    "overflow_v",
    "power_ir_drop_pct",
    "clock_skew_ns",
    "max_transition_ns",
    "max_capacitance_pf",
]


class ResolutionHarvestEngine:
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or _get_db_path()

    def _conn(self):
        return sqlite3.connect(self._db_path)

    def _param_delta(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> Dict[str, Any]:
        deltas = {}
        for key in PARAM_CHANGE_CANDIDATES:
            vb = before.get(key)
            va = after.get(key)
            if vb is not None and va is not None and vb != va:
                deltas[key] = {"before": vb, "after": va, "diff": va - vb}
        return deltas

    def find_run_pairs(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT r1.run_id AS failed_run, r1.design_name, r1.wns AS wns1,
                       r1.tns AS tns1, r1.utilization AS util1, r1.status AS status1,
                       r1.drc_violations AS drc1, r1.lvs_result AS lvs1,
                       r1.cell_count AS cells1, r1.runtime_sec AS runtime1,
                       r1.timestamp AS ts1,
                       r2.run_id AS passed_run, r2.wns AS wns2,
                       r2.tns AS tns2, r2.utilization AS util2, r2.status AS status2,
                       r2.drc_violations AS drc2, r2.lvs_result AS lvs2,
                       r2.cell_count AS cells2, r2.runtime_sec AS runtime2,
                       r2.timestamp AS ts2
                FROM runs r1
                JOIN runs r2 ON r1.design_name = r2.design_name
                WHERE r1.status = 'FAILED'
                  AND r2.status = 'SUCCESS'
                  AND r2.timestamp > r1.timestamp
                ORDER BY r1.design_name, r1.timestamp
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def harvest(self) -> Tuple[int, List[Dict[str, Any]]]:
        pairs = self.find_run_pairs()
        proposed = []
        for pair in pairs:
            before = {
                "wns": pair.get("wns1"),
                "tns": pair.get("tns1"),
                "utilization": pair.get("util1"),
                "drc_violations": pair.get("drc1"),
                "lvs_result": pair.get("lvs1"),
                "cell_count": pair.get("cells1"),
                "runtime_sec": pair.get("runtime1"),
            }
            after = {
                "wns": pair.get("wns2"),
                "tns": pair.get("tns2"),
                "utilization": pair.get("util2"),
                "drc_violations": pair.get("drc2"),
                "lvs_result": pair.get("lvs2"),
                "cell_count": pair.get("cells2"),
                "runtime_sec": pair.get("runtime2"),
            }
            deltas = self._param_delta(before, after)

            design = pair.get("design_name", "")
            failure_type = self._infer_failure_type(before, after)

            if failure_type and deltas:
                pattern = self._propose_pattern(
                    pair["failed_run"],
                    pair["passed_run"],
                    design,
                    failure_type,
                    deltas,
                    before,
                    after,
                )
                proposed.append(pattern)

        inserted = 0
        for p in proposed:
            try:
                self._insert_pattern(p)
                inserted += 1
            except Exception as e:
                log.warning("Failed to insert pattern for %s: %s", p.get("failure_type"), e)

        return inserted, proposed

    def _infer_failure_type(
        self, before: Dict[str, Any], after: Dict[str, Any]
    ) -> Optional[str]:
        bw = before.get("wns")
        aw = after.get("wns")
        bd = before.get("drc_violations")
        ad = after.get("drc_violations")

        if bd is not None and ad is not None and (bd or 0) > (ad or 0):
            return "DRC"
        if bw is not None and aw is not None and bw < -0.1 and aw >= -0.05:
            return "Timing"
        bl = before.get("lvs_result", "")
        al = after.get("lvs_result", "")
        if (not bl or bl.upper() in ("FAIL", "FAILED")) and al and al.upper() == "PASS":
            return "LVS"
        return "UNKNOWN"

    def _propose_pattern(
        self,
        failed_run: str,
        passed_run: str,
        design: str,
        failure_type: str,
        deltas: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> Dict[str, Any]:
        param_change_text = "; ".join(
            f"{k}: {v['before']} -> {v['after']}" for k, v in deltas.items()
        )
        now = datetime.now(timezone.utc).isoformat()
        return {
            "id": str(uuid.uuid4()),
            "failure_fingerprint": f"{failure_type}::{failed_run}",
            "failure_type": failure_type,
            "root_cause": f"Run {failed_run} failed; resolved in {passed_run}",
            "resolution": param_change_text,
            "resolution_type": "PARAMETER_CHANGE",
            "success_count": 1,
            "failure_count": 0,
            "confidence": 0.5,
            "first_seen": now,
            "last_seen": now,
            "created_at": now,
            "updated_at": now,
            "unique_runs": 2,
            "unique_designs": 1,
            "engineer_confirmations": 0,
            "contradictory_reports": 0,
            "trust_score": 0.3,
            "trust_level": "LOW",
            "trust_reason": "AUTO_HARVESTED_PENDING_REVIEW",
            "tracked_run_ids": json.dumps([failed_run, passed_run]),
            "tracked_design_names": json.dumps([design]),
            "design": design,
            "before_metrics": json.dumps(before),
            "after_metrics": json.dumps(after),
        }

    def _insert_pattern(self, pattern: Dict[str, Any]):
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO resolution_patterns
                    (id, failure_fingerprint, failure_type, root_cause, resolution,
                     resolution_type, success_count, failure_count, confidence,
                     first_seen, last_seen, created_at, updated_at,
                     unique_runs, unique_designs, engineer_confirmations,
                     contradictory_reports, trust_score, trust_level,
                     trust_reason, tracked_run_ids, tracked_design_names)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pattern["id"],
                    pattern["failure_fingerprint"],
                    pattern["failure_type"],
                    pattern["root_cause"],
                    pattern["resolution"],
                    pattern["resolution_type"],
                    pattern["success_count"],
                    pattern["failure_count"],
                    pattern["confidence"],
                    pattern["first_seen"],
                    pattern["last_seen"],
                    pattern["created_at"],
                    pattern["updated_at"],
                    pattern["unique_runs"],
                    pattern["unique_designs"],
                    pattern["engineer_confirmations"],
                    pattern["contradictory_reports"],
                    pattern["trust_score"],
                    pattern["trust_level"],
                    pattern["trust_reason"],
                    pattern["tracked_run_ids"],
                    pattern["tracked_design_names"],
                ),
            )
