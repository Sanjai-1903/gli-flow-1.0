"""Week 6: Community Intelligence audit tests."""

from failure_atlas.community_intelligence.escalation import should_escalate
from failure_atlas.community_intelligence.failure_package import FailurePackageBuilder
from failure_atlas.community_intelligence.response_format import (
    EngineeringResponse, KnowledgeContribution,
)


def test_should_escalate_tapeout_blocking():
    result = should_escalate(
        failure_type="HOLD_VIOLATION",
        severity="TAPEOUT_BLOCKING",
        confidence=0.95,
    )
    assert result


def test_should_escalate_user_requested():
    result = should_escalate(
        failure_type="UNKNOWN",
        severity="MEDIUM",
        confidence=0.5,
        user_requested=True,
    )
    assert result


def test_failure_package_builder_minimal():
    pkg = FailurePackageBuilder.build(
        tool="openroad",
        stage="SYNTHESIS",
        failure_type="SETUP_VIOLATION",
        error_text="WNS = -0.5",
    )
    d = pkg.to_dict()
    assert d.get("failure", {}).get("failure_type") == "SETUP_VIOLATION"
    assert d.get("failure", {}).get("tool") == "openroad"
    assert d.get("failure", {}).get("stage") == "SYNTHESIS"


def test_failure_package_sanitized():
    pkg = FailurePackageBuilder.build(
        tool="openroad",
        stage="ROUTING",
        failure_type="DRC",
        error_text="confidential design data",
    )
    errors = pkg.validate_sanitized()
    assert isinstance(errors, list)


def test_engineering_response_roundtrip():
    resp = EngineeringResponse(
        escalation_id="esc_001",
        failure_type="SETUP_VIOLATION",
        signature="WNS=-0.5",
        atlas_id="FA-0001",
        description="Setup timing violated",
        fix_description="Reduce logic depth",
        engineer_name="Test Engineer",
        engineer_email="test@example.com",
        knowledge_contribution=KnowledgeContribution(
            new_signature_created=True,
            atlas_id_assigned="FA-0001",
        ),
    )
    d = resp.to_dict()
    assert d.get("resolution", {}).get("atlas_id") == "FA-0001"

    restored = EngineeringResponse.from_dict(d)
    assert restored.escalation_id == "esc_001"
    assert restored.atlas_id == "FA-0001"
