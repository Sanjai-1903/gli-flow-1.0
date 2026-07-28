"""Week 6: AI Assistant validation tests."""

from failure_atlas.ai_assistant.trigger import should_use_ai, AITriggerResult
from failure_atlas.ai_assistant.response_schema import AIResponse, validate_response


def test_should_use_ai_tapeout_blocking():
    result = should_use_ai(
        failure_type="SETUP_VIOLATION",
        severity="TAPEOUT_BLOCKING",
        confidence=0.9,
    )
    assert isinstance(result, AITriggerResult)
    assert result.use_ai


def test_should_use_ai_returns_reasons():
    result = should_use_ai(
        failure_type="HOLD_VIOLATION",
        severity="TAPEOUT_BLOCKING",
        confidence=0.85,
    )
    assert result.use_ai
    assert isinstance(result.reasons, list)
    assert len(result.reasons) > 0


def test_ai_response_defaults():
    resp = AIResponse()
    assert resp.confidence == "LOW"
    assert resp.summary == ""
    assert resp.disclaimer is True


def test_ai_response_to_dict():
    resp = AIResponse(
        confidence="MEDIUM",
        summary="Clock skew detected",
        possible_causes=["High fanout net"],
    )
    d = resp.to_dict()
    assert "summary" in d
    assert "possible_causes" in d


def test_validate_response_valid():
    data = {"confidence": "LOW", "summary": "test", "possible_causes": [], "disclaimer": True}
    errors = validate_response(data)
    assert len(errors) == 0


def test_validate_response_invalid():
    data = {"confidence": "INVALID", "summary": ""}
    errors = validate_response(data)
    assert len(errors) > 0


def test_heuristic_fallback():
    context = {
        "failure_type": "SETUP_VIOLATION",
        "metrics": {"setup_wns_ns": -0.5},
    }
    resp = AIResponse.heuristic_fallback(context)
    assert resp.confidence == "LOW"
    assert resp.summary
