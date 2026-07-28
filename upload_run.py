from __future__ import annotations
import argparse, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
import httpx


def _flatten_metrics(d):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, (int, float, str, bool)) or v is None:
            out[k] = v
    return out


def load_run(run_dir):
    if not run_dir.is_dir():
        sys.exit(f"Run directory not found: {run_dir}")
    payload = {"run_id": run_dir.name, "source_version": "gli-flow-cli/direct-upload-1.0"}
    metrics_path = run_dir / "telemetry" / "metrics.json"
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    design_name = metrics.get("design_name", "unknown")
    pdk = metrics.get("pdk", "")
    now_iso = datetime.now(timezone.utc).isoformat()
    telemetry_events, failure_entries = [], []

    tele_dir = run_dir / "telemetry"
    if tele_dir.is_dir():
        for stage_file in sorted(tele_dir.glob("*.json")):
            if stage_file.name == "metrics.json":
                continue
            try:
                stage_data = json.loads(stage_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            telemetry_events.append({
                "run_id": payload["run_id"], "tool": "gli-flow",
                "stage": stage_file.stem.upper(), "event": "stage_completed",
                "design_name": design_name,
                "metrics": _flatten_metrics(stage_data),
                "recorded_at": now_iso,
            })

    if metrics:
        telemetry_events.append({
            "run_id": payload["run_id"], "tool": "gli-flow",
            "stage": "SUMMARY", "event": "run_completed",
            "design_name": design_name,
            "metrics": _flatten_metrics(metrics.get("metrics", {})),
            "details": {"pdk": pdk, "pdk_variant": metrics.get("pdk_variant", "")},
            "recorded_at": now_iso,
        })

    ai_path = run_dir / "ai_explanation.json"
    if ai_path.exists():
        try:
            ai = json.loads(ai_path.read_text())
            if ai.get("summary") or ai.get("likely_cause"):
                failure_entries.append({
                    "run_id": payload["run_id"], "tool": "gli-flow", "stage": "UNKNOWN",
                    "failure_type": "AI_EXPLANATION",
                    "error_text": (ai.get("summary") or "")[:1000],
                    "design_name": design_name,
                    "last_seen": now_iso, "detected_at": now_iso,
                })
        except (json.JSONDecodeError, OSError):
            pass

    payload["telemetry_events"] = telemetry_events
    payload["failure_atlas_entries"] = failure_entries
    payload["escalations"] = []
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--server", default=os.environ.get("GLI_SERVER_URL", "http://127.0.0.1:8100"))
    parser.add_argument("--runs-root", default="outputs/runs")
    args = parser.parse_args()
    run_dir = Path(args.runs_root) / args.run_id
    payload = load_run(run_dir)
    print(f"Prepared {len(payload['telemetry_events'])} events + {len(payload['failure_atlas_entries'])} failures for {args.run_id}")
    if not payload["telemetry_events"] and not payload["failure_atlas_entries"]:
        sys.exit("Nothing to upload.")
    url = args.server.rstrip("/") + "/api/v1/telemetry"
    print(f"POST -> {url}")
    r = httpx.post(url, json=payload, timeout=30.0)
    print(f"HTTP {r.status_code}")
    print(r.text[:800])
    r.raise_for_status()
    print("Upload succeeded.")


if __name__ == "__main__":
    main()
