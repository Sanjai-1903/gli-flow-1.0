import dataclasses
from typing import Optional, List, Dict, Any

from failure_atlas.signature_engine import load_signatures, scan_file
from failure_atlas.correlation_engine import get_correlation_data
from failure_atlas.repository import FailureAtlasRepository


KNOWN_SIGNATURES = {
    "licon.8a",
    "hold_violation",
    "power_analysis_failed",
}


@dataclasses.dataclass
class AITriggerResult:
    use_ai: bool
    reasons: List[str]
    signature_match: Optional[str] = None
    historical_count: int = 0
    confidence: float = 0.0


def should_use_ai(
    failure_type: str,
    signature: str = "",
    severity: str = "MEDIUM",
    confidence: float = 0.0,
    log_file: Optional[str] = None,
    run_id: Optional[str] = None,
    repo: Optional[FailureAtlasRepository] = None,
) -> AITriggerResult:
    """Determine if AI investigation should be triggered for a failure.

    AI is now triggered for ALL failures. Known signatures and historical
    data are used to enhance the AI response, not to bypass it.
    """
    reasons = []
    historical_count = 0

    if signature in KNOWN_SIGNATURES:
        reasons.append(f"Known signature: {signature}")
        reasons.append("AI explanation will cite known pattern")

    if signature:
        sigs = load_signatures()
        for s in sigs:
            observed = s.get("observed_signature", "")
            if observed and observed.strip() == signature.strip():
                reasons.append(f"Signature library match: {s.get('atlas_id', 'unknown')}")

    if log_file:
        sigs = load_signatures()
        matches = scan_file(log_file, sigs)
        if matches:
            matched_ids = [m.get("atlas_id", m.get("rule_id", "unknown")) for m in matches]
            reasons.append(f"Signature engine matched: {', '.join(matched_ids)}")

    try:
        correlation = get_correlation_data(failure_type)
        stats = correlation.get("statistics", {})
        historical_count = stats.get("total_occurrences", 0)
        if historical_count > 0:
            resolved = stats.get("resolved_count", 0)
            reasons.append(f"Historical intelligence: {historical_count} occurrences, {resolved} resolved")
    except Exception:
        pass

    if repo:
        try:
            entries = repo.search_entries(failure_type=failure_type, limit=1)
            if entries:
                reasons.append(f"Failure Atlas entry exists for {failure_type}")
        except Exception:
            pass

    if confidence < 0.6:
        reasons.append(f"Confidence: {confidence:.2f}")

    if not reasons:
        reasons.append("Unknown failure — no signature, no historical data")

    reasons.append("Triggering AI Investigation Assistant")
    return AITriggerResult(
        use_ai=True,
        reasons=reasons,
        signature_match=signature if signature in KNOWN_SIGNATURES else None,
        historical_count=historical_count,
        confidence=confidence,
    )
