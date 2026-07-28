"""
Execution Intelligence Data Model.

Failure Atlas evolves beyond static knowledge.
Stores observed evidence, tool output, metrics, and resolution effectiveness.
Becomes future GLI-SDI training data.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class ObservedFailure:
    failure_id: str
    run_id: str
    tool_name: str
    tool_version: str
    tool_stage: str
    failure_hash: str
    severity: str
    observed_evidence: dict[str, Any] = field(default_factory=dict)
    tool_output: str = ""
    metrics_before: dict[str, Any] = field(default_factory=dict)
    metrics_after: dict[str, Any] = field(default_factory=dict)
    resolution_attempted: bool = False
    resolution_successful: bool = False
    resolution_type: str = ""
    environment_fingerprint: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DerivedFailurePattern:
    pattern_id: str
    failure_signature: str
    tool_name: str
    tool_stage: str
    occurrence_count: int
    first_seen: str
    last_seen: str
    common_evidence: dict[str, Any] = field(default_factory=dict)
    associated_metrics: dict[str, Any] = field(default_factory=dict)
    resolution_success_rate: float = 0.0
    recommended_resolution: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResolutionPattern:
    pattern_id: str
    failure_pattern_id: str
    resolution_type: str
    resolution_steps: list[str] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    avg_runtime_impact_s: float = 0.0
    avg_qor_impact: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionSignature:
    signature_id: str
    run_id: str
    design_name: str
    toolchain: str
    pdk: str
    stages_completed: list[str] = field(default_factory=list)
    stages_failed: list[str] = field(default_factory=list)
    total_runtime_s: float = 0.0
    qor_score: float = 0.0
    failure_hashes: list[str] = field(default_factory=list)
    environment_fingerprint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExecutionIntelligenceDB:
    def __init__(self):
        self.observed_failures: list[ObservedFailure] = []
        self.derived_patterns: dict[str, DerivedFailurePattern] = {}
        self.resolution_patterns: dict[str, ResolutionPattern] = {}

    def record_failure(self, failure: ObservedFailure) -> None:
        self.observed_failures.append(failure)
        self._update_patterns(failure)

    def _update_patterns(self, failure: ObservedFailure) -> None:
        sig = f"{failure.tool_name}::{failure.tool_stage}::{failure.failure_hash}"
        if sig in self.derived_patterns:
            pattern = self.derived_patterns[sig]
            pattern.occurrence_count += 1
            pattern.last_seen = failure.timestamp
            if failure.resolution_successful:
                pattern.resolution_success_rate = (
                    (pattern.resolution_success_rate * (pattern.occurrence_count - 1) + 1.0)
                    / pattern.occurrence_count
                )
        else:
            pattern = DerivedFailurePattern(
                pattern_id=sig,
                failure_signature=failure.failure_hash,
                tool_name=failure.tool_name,
                tool_stage=failure.tool_stage,
                occurrence_count=1,
                first_seen=failure.timestamp,
                last_seen=failure.timestamp,
                common_evidence=failure.observed_evidence,
                associated_metrics=failure.metrics_before,
            )
            self.derived_patterns[sig] = pattern

    def get_patterns_by_tool(self, tool_name: str) -> list[DerivedFailurePattern]:
        return [
            p for p in self.derived_patterns.values()
            if p.tool_name == tool_name
        ]

    def get_high_impact_patterns(self, min_occurrences: int = 3) -> list[DerivedFailurePattern]:
        return [
            p for p in self.derived_patterns.values()
            if p.occurrence_count >= min_occurrences
        ]

    def export_training_data(self) -> dict[str, Any]:
        return {
            "observed_failures": [f.to_dict() for f in self.observed_failures],
            "derived_patterns": [p.to_dict() for p in self.derived_patterns.values()],
            "resolution_patterns": [r.to_dict() for r in self.resolution_patterns.values()],
        }
