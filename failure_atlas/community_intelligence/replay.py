import json
import os
import sys
from datetime import datetime
from typing import Optional


class TelemetryReplayEngine:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            from gli_flow.database.migrations import _get_db_path
            self.db_path = _get_db_path()
        self.results = {
            "replay_metadata": {
                "started_at": None,
                "completed_at": None,
                "source_file": None,
                "total_events": 0,
                "successful": 0,
                "failed": 0,
            },
            "events": [],
            "failures": [],
            "resolutions": [],
            "timeline": [],
        }

    def load_export(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Export file not found: {filepath}")
        with open(filepath) as f:
            return json.load(f)

    def replay(self, filepath: str, dry_run: bool = True) -> dict:
        self.results["replay_metadata"]["started_at"] = datetime.utcnow().isoformat()
        self.results["replay_metadata"]["source_file"] = filepath

        data = self.load_export(filepath)
        export_meta = data.get("export_metadata", {})

        telemetry = data.get("telemetry_events", [])
        unknowns = data.get("failure_atlas_entries", data.get("unknown_failures", []))
        escalations = data.get("escalations", [])
        patterns = data.get("resolution_patterns", [])

        self.results["replay_metadata"]["total_events"] = (
            len(telemetry) + len(unknowns) + len(escalations) + len(patterns)
        )

        for evt in telemetry:
            self._replay_event(evt, dry_run)
        for unk in unknowns:
            self._replay_unknown(unk, dry_run)
        for esc in escalations:
            self._replay_escalation(esc, dry_run)
        for pat in patterns:
            self._replay_pattern(pat, dry_run)

        self.results["replay_metadata"]["completed_at"] = datetime.utcnow().isoformat()
        return self.results

    def _replay_event(self, evt: dict, dry_run: bool):
        event_name = evt.get("event", "unknown")
        self.results["events"].append({
            "event": event_name,
            "status": "simulated" if dry_run else "recorded",
            "dry_run": dry_run,
            "details": evt,
        })
        self.results["timeline"].append({
            "type": "telemetry_event",
            "name": event_name,
            "timestamp": evt.get("created_at", ""),
            "status": "simulated" if dry_run else "recorded",
        })
        self.results["replay_metadata"]["successful"] += 1

        if not dry_run:
            from failure_atlas.community_intelligence import EscalationTelemetry
            telemetry = EscalationTelemetry(self.db_path)
            telemetry.record(
                event=evt.get("event", ""),
                escalation_id=evt.get("escalation_id", ""),
                failure_type=evt.get("failure_type", ""),
                tool=evt.get("tool", ""),
                atlas_id=evt.get("atlas_id", ""),
                details=evt.get("details", {}),
            )

    def _replay_unknown(self, unk: dict, dry_run: bool):
        self.results["failures"].append({
            "tool": unk.get("tool", ""),
            "failure_type": unk.get("failure_type", ""),
            "signature": unk.get("signature", ""),
            "frequency": unk.get("frequency", 0),
            "status": "simulated" if dry_run else "recorded",
            "dry_run": dry_run,
        })
        self.results["timeline"].append({
            "type": "unknown_failure",
            "name": f"{unk.get('tool', '')}:{unk.get('failure_type', '')}",
            "timestamp": unk.get("last_seen", ""),
            "status": "simulated" if dry_run else "recorded",
        })
        self.results["replay_metadata"]["successful"] += 1

    def _replay_escalation(self, esc: dict, dry_run: bool):
        self.results["resolutions"].append({
            "id": esc.get("id", ""),
            "failure_type": esc.get("failure_type", ""),
            "status": esc.get("status", ""),
            "dry_run": dry_run,
        })
        self.results["timeline"].append({
            "type": "escalation",
            "name": esc.get("failure_type", ""),
            "timestamp": esc.get("created_at", ""),
            "status": "simulated" if dry_run else "recorded",
        })
        self.results["replay_metadata"]["successful"] += 1

    def _replay_pattern(self, pat: dict, dry_run: bool):
        self.results["resolutions"].append({
            "fingerprint": pat.get("failure_fingerprint", ""),
            "resolution": pat.get("resolution", ""),
            "confidence": pat.get("confidence", 0.0),
            "dry_run": dry_run,
        })
        self.results["timeline"].append({
            "type": "resolution_pattern",
            "name": pat.get("failure_fingerprint", "")[:40],
            "timestamp": pat.get("last_seen", ""),
            "status": "simulated" if dry_run else "recorded",
        })
        self.results["replay_metadata"]["successful"] += 1

    def summary_text(self) -> str:
        meta = self.results["replay_metadata"]
        lines = [
            f"Replay Summary",
            f"  Source:      {meta['source_file']}",
            f"  Started:     {meta['started_at']}",
            f"  Completed:   {meta['completed_at']}",
            f"  Total:       {meta['total_events']}",
            f"  Successful:  {meta['successful']}",
            f"  Failed:      {meta['failed']}",
            f"  Dry run:     {all(e.get('dry_run', True) for e in self.results['events'] + self.results['failures'] + self.results['resolutions'])}",
        ]
        return "\n".join(lines)
