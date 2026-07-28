import os

from gli_flow.database.factory import create_provider
from gli_flow.database.migrations import _get_db_path


class DatabaseManager:

    def __init__(self, db_path=None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = _get_db_path()
        supabase_token = os.environ.get("SUPABASE_API_TOKEN")
        supabase_ref = os.environ.get("SUPABASE_PROJECT_REF")
        if supabase_token and supabase_ref:
            self._provider = create_provider()
        else:
            self._provider = create_provider(db_path=self.db_path)

    def update_run_signoff(self, run_id, signoff_gate=None, timing_result=None, drc_result=None, lvs_result=None):
        import dataclasses
        import json as json_mod
        self._provider.execute("""
            UPDATE runs SET
                drc_magic_violations = ?,
                drc_klayout_violations = ?,
                drc_is_clean = ?,
                lvs_result = ?,
                lvs_is_clean = ?,
                setup_wns_ns = ?,
                hold_whs_ns = ?,
                signoff_setup_pass = ?,
                signoff_hold_pass = ?,
                signoff_gate_json = ?,
                tapeout_ready = ?
            WHERE run_id = ?
        """, (
            drc_result.magic_violations if drc_result else None,
            drc_result.klayout_violations if drc_result else None,
            drc_result.is_clean if drc_result else False,
            lvs_result.result if lvs_result else "NOT_RUN",
            lvs_result.is_clean if lvs_result else False,
            timing_result.setup_wns_ns if timing_result else None,
            timing_result.hold_whs_ns if timing_result else None,
            signoff_gate.setup_pass if signoff_gate else False,
            signoff_gate.hold_pass if signoff_gate else False,
            json_mod.dumps(dataclasses.asdict(signoff_gate)) if signoff_gate else "{}",
            signoff_gate.tapeout_ready if signoff_gate else False,
            run_id,
        ))

    def execute(self, sql, params=None):
        self._provider.execute(sql, params)

    def close(self):
        if self._provider:
            self._provider.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert_run(self, record):
        self._provider.execute(
            """
            INSERT INTO runs (
                run_id, design_name, status, current_stage,
                progress, wns, tns, utilization, runtime_sec,
                cell_count, qor_score, run_dir
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.run_id, record.design_name, record.status,
                record.current_stage, record.progress,
                record.wns, record.tns, record.utilization,
                record.runtime_sec, record.cell_count, record.qor_score,
                str(getattr(record, 'run_dir', '')),
            ),
        )

    def update_run(self, run_id, status=None, current_stage=None, progress=None,
                   wns=None, tns=None, utilization=None, runtime_sec=None,
                   cell_count=None, qor_score=None, run_dir=None,
                   hold_wns=None, hold_tns=None,
                   implementation_status=None, signoff_status=None,
                   implementation_score=None, signoff_score=None,
                   tapeout_ready=None, root_cause_summary=None,
                   drc_violations=None, drc_is_clean=None, lvs_result=None, lvs_is_clean=None,
                   signoff_setup_pass=None, signoff_hold_pass=None):
        fields = []
        values = []

        if status is not None:
            fields.append("status = ?")
            values.append(status)
        if current_stage is not None:
            fields.append("current_stage = ?")
            values.append(current_stage)
        if progress is not None:
            fields.append("progress = ?")
            values.append(progress)
        if wns is not None:
            fields.append("wns = ?")
            values.append(wns)
        if tns is not None:
            fields.append("tns = ?")
            values.append(tns)
        if hold_wns is not None:
            fields.append("hold_wns = ?")
            values.append(hold_wns)
        if hold_tns is not None:
            fields.append("hold_tns = ?")
            values.append(hold_tns)
        if utilization is not None:
            fields.append("utilization = ?")
            values.append(utilization)
        if runtime_sec is not None:
            fields.append("runtime_sec = ?")
            values.append(runtime_sec)
        if cell_count is not None:
            fields.append("cell_count = ?")
            values.append(cell_count)
        if qor_score is not None:
            fields.append("qor_score = ?")
            values.append(qor_score)
        if run_dir is not None:
            fields.append("run_dir = ?")
            values.append(run_dir)
        if implementation_status is not None:
            fields.append("implementation_status = ?")
            values.append(implementation_status)
        if signoff_status is not None:
            fields.append("signoff_status = ?")
            values.append(signoff_status)
        if implementation_score is not None:
            fields.append("implementation_score = ?")
            values.append(implementation_score)
        if signoff_score is not None:
            fields.append("signoff_score = ?")
            values.append(signoff_score)
        if tapeout_ready is not None:
            fields.append("tapeout_ready = ?")
            values.append(tapeout_ready)
        if root_cause_summary is not None:
            fields.append("root_cause_summary = ?")
            values.append(root_cause_summary)
        if drc_violations is not None:
            fields.append("drc_violations = ?")
            values.append(drc_violations)
        if drc_is_clean is not None:
            fields.append("drc_is_clean = ?")
            values.append(drc_is_clean)
        if lvs_result is not None:
            fields.append("lvs_result = ?")
            values.append(lvs_result)
        if lvs_is_clean is not None:
            fields.append("lvs_is_clean = ?")
            values.append(lvs_is_clean)
        if signoff_setup_pass is not None:
            fields.append("signoff_setup_pass = ?")
            values.append(signoff_setup_pass)
        if signoff_hold_pass is not None:
            fields.append("signoff_hold_pass = ?")
            values.append(signoff_hold_pass)

        if not fields:
            return

        values.append(run_id)

        self._provider.execute(
            f"UPDATE runs SET {', '.join(fields)} WHERE run_id = ?",
            values,
        )

    def get_recent_runs(self, limit=20):
        rows = self._provider.fetchall(
            """
            SELECT run_id, design_name, qor_score,
                   wns, tns, utilization, runtime_sec, cell_count,
                   status, current_stage, progress, timestamp
            FROM runs
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [
            {
                "run_id": row["run_id"],
                "design_name": row["design_name"],
                "qor_score": row["qor_score"],
                "wns": row["wns"],
                "tns": row["tns"],
                "utilization": row["utilization"],
                "runtime_sec": row["runtime_sec"],
                "cell_count": row["cell_count"],
                "status": row["status"],
                "current_stage": row["current_stage"],
                "progress": row["progress"],
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    def get_runs_for_design(self, design_name, limit=10):
        rows = self._provider.fetchall(
            """
            SELECT run_id, design_name, qor_score,
                   wns, tns, utilization, runtime_sec, cell_count,
                   status, current_stage, progress, timestamp
            FROM runs
            WHERE design_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (design_name, limit),
        )
        return [
            {
                "run_id": row["run_id"],
                "design_name": row["design_name"],
                "qor_score": row["qor_score"],
                "wns": row["wns"],
                "tns": row["tns"],
                "utilization": row["utilization"],
                "runtime_sec": row["runtime_sec"],
                "cell_count": row["cell_count"],
                "status": row["status"],
                "current_stage": row["current_stage"],
                "progress": row["progress"],
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    def get_run(self, run_id):
        row = self._provider.fetchone(
            """
            SELECT run_id, design_name, qor_score,
                   wns, tns, utilization, runtime_sec, cell_count,
                   status, current_stage, progress, timestamp,
                   run_dir, regression, drc_violations, lvs_result
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        )
        if row is None:
            return None
        return {
            "run_id": row["run_id"],
            "design_name": row["design_name"],
            "qor_score": row["qor_score"],
            "wns": row["wns"],
            "tns": row["tns"],
            "utilization": row["utilization"],
            "runtime_sec": row["runtime_sec"],
            "cell_count": row["cell_count"],
            "status": row["status"],
            "current_stage": row["current_stage"],
            "progress": row["progress"],
            "timestamp": row["timestamp"],
            "run_dir": row["run_dir"],
            "regression": row["regression"],
            "drc_violations": row["drc_violations"],
            "lvs_result": row["lvs_result"],
        }

    def get_qor_trend(self, limit=20):
        rows = self._provider.fetchall(
            """
            SELECT qor_score, wns, tns, utilization, timestamp
            FROM runs
            WHERE qor_score IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [
            {
                "qor_score": row["qor_score"],
                "wns": row["wns"],
                "tns": row["tns"],
                "utilization": row["utilization"],
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    def update_run_investigation(self, run_id, available=None, status=None, summary=None, timestamp=None, failed_attempts=None):
        fields = []
        values = []
        if available is not None:
            fields.append("llm_investigation_available = ?")
            values.append(available)
        if status is not None:
            fields.append("llm_investigation_status = ?")
            values.append(status)
        if summary is not None:
            fields.append("llm_investigation_summary = ?")
            values.append(summary)
        if timestamp is not None:
            fields.append("llm_investigation_timestamp = ?")
            values.append(timestamp)
        if failed_attempts is not None:
            fields.append("llm_investigation_failed_attempts = ?")
            values.append(failed_attempts)
        if not fields:
            return
        values.append(run_id)
        self._provider.execute(
            f"UPDATE runs SET {', '.join(fields)} WHERE run_id = ?",
            values,
        )

    def get_run_investigation_row(self, run_id):
        return self._provider.fetchone(
            """SELECT llm_investigation_available, llm_investigation_status,
               llm_investigation_summary, llm_investigation_timestamp,
               llm_investigation_failed_attempts
               FROM runs WHERE run_id = ?""",
            (run_id,),
        )

    def get_last_successful_run(self, design_name):
        row = self._provider.fetchone(
            """
            SELECT run_id, design_name, qor_score,
                   wns, tns, utilization, runtime_sec, cell_count,
                   status, current_stage, progress, timestamp
            FROM runs
            WHERE design_name = ? AND status = 'SUCCESS'
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (design_name,),
        )
        if row is None:
            return None
        return {
            "run_id": row["run_id"],
            "design_name": row["design_name"],
            "qor_score": row["qor_score"],
            "wns": row["wns"],
            "tns": row["tns"],
            "utilization": row["utilization"],
            "runtime_sec": row["runtime_sec"],
            "cell_count": row["cell_count"],
            "status": row["status"],
            "current_stage": row["current_stage"],
            "progress": row["progress"],
            "timestamp": row["timestamp"],
        }
