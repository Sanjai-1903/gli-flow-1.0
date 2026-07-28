"""
Failure Atlas V2 Schema Extension.

Extends the existing schema with:
  - failure_hash (SHA256 of tool + stage + signature + evidence)
  - tool_name, tool_version, tool_stage
  - first_seen, last_seen, occurrence_count
  - environment_fingerprint
  - resolution_attempts, resolution_success_rate
  - regression_detected
  - artifact_snapshot, execution_snapshot, timing_snapshot
  - utilization_snapshot, congestion_snapshot, runtime_snapshot

Duplicate failures collapse into canonical atlas entries.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def generate_failure_hash(
    tool: str,
    stage: str,
    signature: str,
    evidence: str,
) -> str:
    raw = f"{tool}::{stage}::{signature}::{evidence}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass
class FailureV2Entry:
    failure_hash: str
    tool_name: str
    tool_version: str
    tool_stage: str
    first_seen: str
    last_seen: str
    occurrence_count: int
    environment_fingerprint: Optional[str] = None
    resolution_attempts: int = 0
    resolution_success_rate: float = 0.0
    regression_detected: bool = False
    artifact_snapshot: Optional[dict] = None
    execution_snapshot: Optional[dict] = None
    timing_snapshot: Optional[dict] = None
    utilization_snapshot: Optional[dict] = None
    congestion_snapshot: Optional[dict] = None
    runtime_snapshot: Optional[dict] = None

    @classmethod
    def from_failure(
        cls,
        tool: str,
        stage: str,
        signature: str,
        evidence: str,
        tool_version: str = "",
        env_fingerprint: str = None,
    ) -> "FailureV2Entry":
        fhash = generate_failure_hash(tool, stage, signature, evidence)
        now = time.strftime("%Y-%m-%dT%H:%M:%S")
        return cls(
            failure_hash=fhash,
            tool_name=tool,
            tool_version=tool_version,
            tool_stage=stage,
            first_seen=now,
            last_seen=now,
            occurrence_count=1,
            environment_fingerprint=env_fingerprint,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k in ("artifact_snapshot", "execution_snapshot", "timing_snapshot",
                   "utilization_snapshot", "congestion_snapshot", "runtime_snapshot"):
            if isinstance(d.get(k), dict):
                d[k] = json.dumps(d[k])
        return d


def collapse_duplicates(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    canonical: dict[str, dict[str, Any]] = {}
    for entry in entries:
        fhash = entry.get("failure_hash") or generate_failure_hash(
            entry.get("tool_name", ""),
            entry.get("tool_stage", ""),
            entry.get("signature", ""),
            json.dumps(entry.get("evidence", {}), sort_keys=True),
        )
        if fhash in canonical:
            existing = canonical[fhash]
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            existing["last_seen"] = entry.get("detected_at", time.strftime("%Y-%m-%dT%H:%M:%S"))
            if entry.get("regression_detected"):
                existing["regression_detected"] = True
        else:
            entry["failure_hash"] = fhash
            canonical[fhash] = entry
    return list(canonical.values())
