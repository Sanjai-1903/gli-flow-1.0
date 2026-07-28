from failure_atlas.schema import FailureAtlasEntry
from failure_atlas.detector import detect_failures
from failure_atlas.taxonomy import FailureDomain, FailureCategory, FailureSeverity
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.signature_engine import load_signatures, scan_file

from failure_atlas.ai_assistant import (
    should_use_ai, AITriggerResult,
    build_context, AIContext,
    AIResponse, validate_response,
    FeedbackStore,
    ResolutionCapture,
)

from failure_atlas.community_intelligence import (
    EscalationManager, EscalationRecord, should_escalate,
    FailurePackageBuilder, FailurePackage,
    EngineeringResponse, KnowledgeContribution,
    EscalationTelemetry,
    UnknownFailureDataset,
)

__all__ = [
    "FailureAtlasEntry", "detect_failures",
    "FailureDomain", "FailureCategory", "FailureSeverity",
    "FailureAtlasRepository", "load_signatures", "scan_file",
    "should_use_ai", "AITriggerResult",
    "build_context", "AIContext",
    "AIResponse", "validate_response",
    "FeedbackStore",
    "ResolutionCapture",
    "EscalationManager", "EscalationRecord", "should_escalate",
    "FailurePackageBuilder", "FailurePackage",
    "EngineeringResponse", "KnowledgeContribution",
    "EscalationTelemetry",
    "UnknownFailureDataset",
]
