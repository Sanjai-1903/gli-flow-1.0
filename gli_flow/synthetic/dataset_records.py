from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import json
from datetime import datetime

@dataclass
class FailureTrainingRecord:
    """
    Represents a single record of a failed execution for training purposes.
    """
    failure_fingerprint: str
    failure_type: str # e.g., "timing_violation", "drc_violation", "lvs_mismatch"
    tool: str # e.g., "openroad", "magic", "netgen"
    stage: str # e.g., "placement", "routing", "lvs"
    telemetry_summary: Dict[str, Any] # Summary of relevant telemetry
    root_cause: str # Discovered root cause
    resolution: str # Recommended resolution
    trust_score: float # Trust score for the label/record

    @staticmethod
    def calculate_fingerprint(data: Dict[str, Any]) -> str:
        """Calculates a unique fingerprint for a failure record based on key attributes."""
        # Use a subset of fields that define the unique nature of the failure
        # Exclude resolution and trust_score as they are outcomes/labels
        relevant_data = {
            "failure_type": data.get("failure_type"),
            "tool": data.get("tool"),
            "stage": data.get("stage"),
            "telemetry_summary": json.dumps(data.get("telemetry_summary", {}), sort_keys=True),
            "root_cause": data.get("root_cause"),
        }
        raw = json.dumps(relevant_data, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

@dataclass
class ValidatedResolutionRecord:
    """
    Records the validation of a resolution applied to a failure.
    """
    failure_fingerprint: str
    fix_applied: str
    outcome: str
    re_run_status: str
    qor_improvement: float

@dataclass
class ResolutionTrainingRecord:
    failure_fingerprint: str
    fix_applied: str
    outcome: str
    metrics_after_fix: Dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    failure_count: int = 0
    trust_score: float = 0.5


@dataclass
class QoREvolutionRecord:
    """
    Records trajectories of QoR metrics based on parameter changes.
    """
    design_name: str
    trajectory_id: str
    metrics_trajectory: List[Dict[str, Any]] # List of {param: ..., qor: ...}


@dataclass
class QoRTrainingRecord:
    """
    Records changes in QoR based on parameter variations.
    """
    design_name: str
    parameter_changes: Dict[str, Any] # Parameters that were varied
    qor_changes: Dict[str, Any] # Changes in QoR metrics (area, power, timing, density, congestion)
    pre_qor_metrics: Dict[str, Any] = field(default_factory=dict)
    post_qor_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphTrainingRecord:
    """
    Records privacy-safe graph features of a design.
    """
    design_name: str
    graph_features: Dict[str, Any] # e.g., fanout distributions, logic depth, resource histograms
    fingerprint: str # Fingerprint of the design for traceability

@dataclass
class TrainingDataset:
    """
    A collection of various training records.
    """
    failure_records: List[FailureTrainingRecord] = field(default_factory=list)
    resolution_records: List[ResolutionTrainingRecord] = field(default_factory=list)
    qor_records: List[QoRTrainingRecord] = field(default_factory=list)
    graph_records: List[GraphTrainingRecord] = field(default_factory=list)
