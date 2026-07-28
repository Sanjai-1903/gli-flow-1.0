import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from failure_atlas.taxonomy import FailureDomain, FailureCategory, FailureSeverity, IncidentType

@dataclass
class DRCViolation:
    rule_name: str
    layer: str
    x1: float
    y1: float
    x2: float
    y2: float
    description: str = ""

@dataclass
class FailureAtlasEntry:
    run_id: str
    detection_stage: str
    level1_domain: FailureDomain
    level2_category: FailureCategory
    level3_signature: str
    severity: FailureSeverity
    incident_type: IncidentType = IncidentType.DESIGN_FAILURE
    atlas_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    origin_stage: Optional[str] = None
    confidence: float = 0.8
    verified_by: str = "AUTOMATED_RULE"
    flow_type: str = "OPEN_SOURCE"
    detection_classification: str = "UNVERIFIED"
    pdk_name: str = ""
    design_name: str = ""
    design_category: str = ""
    pre_failure_metrics: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    spatial_locations: List[Dict[str, Any]] = field(default_factory=list)
    fix_applied: bool = False
    fix_type: Optional[str] = None
    fix_description: Optional[str] = None
    fix_run_id: Optional[str] = None
    # Remediation Engine V1 Fields
    failure_explanation: Optional[str] = None
    root_cause_candidates: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    resolution_history: List[Dict[str, Any]] = field(default_factory=list)
    fix_attempt_count: int = 0
    effective_fixes: List[str] = field(default_factory=list)
