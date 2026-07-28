"""
QoR Intelligence Foundation.

Converts static QoR playbook entries into structured QoRTechnique objects
with telemetry hooks for tracking effectiveness.

Supports:
  Timing improvement attempts
  Congestion reduction attempts
  Area reduction attempts
  Power reduction attempts

Stores before/after metrics for future optimization intelligence.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class QoRCategory(Enum):
    TIMING = "timing"
    CONGESTION = "congestion"
    AREA = "area"
    POWER = "power"
    ROUTING = "routing"
    DRC = "drc"
    LVS = "lvs"
    GENERAL = "general"


class RiskProfile(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class QoRTechnique:
    technique_id: str
    category: QoRCategory
    stage: str
    name: str
    description: str
    applicability_conditions: dict[str, Any] = field(default_factory=dict)
    expected_metric_targets: dict[str, float] = field(default_factory=dict)
    required_inputs: list[str] = field(default_factory=list)
    risk_profile: RiskProfile = RiskProfile.MEDIUM
    evidence_requirements: list[str] = field(default_factory=list)
    execution_history: list[dict[str, Any]] = field(default_factory=list)
    observed_success_rate: float = 0.0
    future_recommendation_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["risk_profile"] = self.risk_profile.value
        return d

    def record_attempt(self, before_metrics: dict, after_metrics: dict, success: bool) -> None:
        self.execution_history.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "before": before_metrics,
            "after": after_metrics,
            "success": success,
        })
        self._recompute_success_rate()

    def _recompute_success_rate(self) -> None:
        if not self.execution_history:
            self.observed_success_rate = 0.0
            return
        successes = sum(1 for h in self.execution_history if h["success"])
        self.observed_success_rate = successes / len(self.execution_history)


TIMING_TECHNIQUES: list[QoRTechnique] = [
    QoRTechnique(
        technique_id="TIMING_001",
        category=QoRCategory.TIMING,
        stage="SYNTHESIS",
        name="Pipeline insertion",
        description="Insert pipeline registers on critical timing paths",
        applicability_conditions={"wns": "< 0", "max_fanout": "> 32"},
        expected_metric_targets={"wns_improvement_ns": 0.5},
        required_inputs=["sdc", "netlist"],
        risk_profile=RiskProfile.LOW,
        evidence_requirements=["pre_synth_timing.rpt", "post_synth_timing.rpt"],
    ),
    QoRTechnique(
        technique_id="TIMING_002",
        category=QoRCategory.TIMING,
        stage="PLACEMENT",
        name="High-fanout buffer tree",
        description="Build buffer trees for high-fanout nets before clock tree synthesis",
        applicability_conditions={"max_fanout": "> 64"},
        expected_metric_targets={"transition_improvement_ns": 0.3},
        required_inputs=["placed.def", "sdc"],
        risk_profile=RiskProfile.LOW,
    ),
    QoRTechnique(
        technique_id="TIMING_003",
        category=QoRCategory.TIMING,
        stage="CTS",
        name="Clock skew optimization",
        description="Balance clock tree to reduce skew across critical paths",
        applicability_conditions={"skew_ns": "> 0.1"},
        expected_metric_targets={"skew_reduction_ns": 0.05},
        required_inputs=["cts.def", "sdc"],
        risk_profile=RiskProfile.MEDIUM,
    ),
]

CONGESTION_TECHNIQUES: list[QoRTechnique] = [
    QoRTechnique(
        technique_id="CONGESTION_001",
        category=QoRCategory.CONGESTION,
        stage="ROUTING",
        name="Global route congestion reduction",
        description="Increase wire spread factor and add routing blockages",
        applicability_conditions={"overflow_pct": "> 5"},
        expected_metric_targets={"overflow_reduction_pct": 3},
        required_inputs=["global.rpt"],
        risk_profile=RiskProfile.LOW,
    ),
]

AREA_TECHNIQUES: list[QoRTechnique] = [
    QoRTechnique(
        technique_id="AREA_001",
        category=QoRCategory.AREA,
        stage="SYNTHESIS",
        name="Resource sharing",
        description="Enable resource sharing and operator merging in synthesis",
        applicability_conditions={"cell_count": "> 10000"},
        expected_metric_targets={"area_reduction_pct": 10},
        required_inputs=["synth.rpt"],
        risk_profile=RiskProfile.LOW,
    ),
]

POWER_TECHNIQUES: list[QoRTechnique] = [
    QoRTechnique(
        technique_id="POWER_001",
        category=QoRCategory.POWER,
        stage="SYNTHESIS",
        name="Clock gating insertion",
        description="Insert clock gating cells to reduce dynamic power",
        applicability_conditions={"total_power_mw": "> 100"},
        expected_metric_targets={"dynamic_power_reduction_pct": 15},
        required_inputs=["synth.rpt", "activity.fsdb"],
        risk_profile=RiskProfile.LOW,
    ),
]

ALL_TECHNIQUES: dict[str, QoRTechnique] = {}


def _register_all():
    for t in TIMING_TECHNIQUES + CONGESTION_TECHNIQUES + AREA_TECHNIQUES + POWER_TECHNIQUES:
        ALL_TECHNIQUES[t.technique_id] = t


_register_all()


def get_technique(technique_id: str) -> Optional[QoRTechnique]:
    return ALL_TECHNIQUES.get(technique_id)


def get_techniques_by_category(category: QoRCategory) -> list[QoRTechnique]:
    return [t for t in ALL_TECHNIQUES.values() if t.category == category]


def get_techniques_by_stage(stage: str) -> list[QoRTechnique]:
    return [t for t in ALL_TECHNIQUES.values() if t.stage == stage]


def recommend_techniques(metrics: dict[str, Any], stage: str) -> list[QoRTechnique]:
    candidates = get_techniques_by_stage(stage)
    recommended = []
    for t in candidates:
        conditions_met = True
        for key, condition in t.applicability_conditions.items():
            actual = metrics.get(key)
            if actual is None:
                continue
            if "<" in condition:
                threshold = float(condition.split("<")[1].strip())
                if isinstance(actual, (int, float)):
                    if not (actual < threshold):
                        conditions_met = False
            elif ">" in condition:
                threshold = float(condition.split(">")[1].strip())
                if isinstance(actual, (int, float)):
                    if not (actual > threshold):
                        conditions_met = False
            elif "==" in condition:
                threshold = condition.split("==")[1].strip()
                if str(actual) != threshold:
                    conditions_met = False
        if conditions_met:
            t.future_recommendation_score = t.observed_success_rate
            recommended.append(t)
    recommended.sort(key=lambda t: t.future_recommendation_score, reverse=True)
    return recommended


def save_qor_intelligence(path: str) -> str:
    data = {
        "techniques": [t.to_dict() for t in ALL_TECHNIQUES.values()],
    }
    Path(path).write_text(json.dumps(data, indent=2))
    return path
