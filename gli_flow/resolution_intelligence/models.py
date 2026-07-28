"""Dataclasses for Resolution Intelligence."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ResolutionPattern:
    id: str
    failure_fingerprint: str
    failure_type: str
    root_cause: Optional[str] = None
    resolution: str = ""
    resolution_type: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.0
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # Trust tracking fields
    unique_runs: int = 0
    unique_designs: int = 0
    engineer_confirmations: int = 0
    contradictory_reports: int = 0
    trust_score: float = 0.0
    trust_level: str = "LOW"
    trust_reason: str = ""
    tracked_run_ids: str = "[]"
    tracked_design_names: str = "[]"

    @property
    def total_attempts(self) -> int:
        return self.success_count + self.failure_count


@dataclass
class ResolutionFeedback:
    id: str
    pattern_id: str
    run_id: str
    feedback_type: str  # "confirmed" or "rejected"
    created_at: str


@dataclass
class ResolutionCandidate:
    failure_fingerprint: str
    failure_type: str
    resolution: str
    confidence: float
    occurrence_count: int
    first_seen: str
    last_seen: str


@dataclass
class RunComparison:
    run_id_a: str
    run_id_b: str
    fields: dict = field(default_factory=dict)
    config_changes: dict = field(default_factory=dict)
    parameter_changes: dict = field(default_factory=dict)
    qor_changes: dict = field(default_factory=dict)
    failure_diffs: list = field(default_factory=list)
