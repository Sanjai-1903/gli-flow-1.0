"""Tests for the LLM Investigation Layer."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from gli_flow.investigation.context_builder import InvestigationContextBuilder
from gli_flow.investigation.prompt_template import get_system_prompt
from gli_flow.investigation.schema import InvestigationSchema, ValidationResult
from gli_flow.investigation.providers.bharatcode import BharatCodeProvider, ProviderResponse
from gli_flow.investigation.investigator import InvestigationLayer, InvestigationResult


class TestContextBuilder:

    def test_build_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            builder = InvestigationContextBuilder(tmp)
            context = builder.build()
            assert context["run_id"] == Path(tmp).name
            assert "No DRC data" in context["drc_summary"]
            assert "No LVS data" in context["lvs_summary"]
            assert "No timing data" in context["timing_summary"]

    def test_build_with_drc_lvs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            drc_lvs = {"drc": {"total_violations": 6, "is_clean": False, "by_rule": {"li.3": 4, "licon.8a": 2}}, "lvs": {"result": "TIMEOUT", "is_clean": False}}
            Path(tmp, "drc_lvs_summary.json").write_text(json.dumps(drc_lvs))
            builder = InvestigationContextBuilder(tmp)
            context = builder.build()
            assert "6" in context["drc_summary"]
            assert "TIMEOUT" in context["lvs_summary"]

    def test_build_context_contains_no_blocked_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "design.v").write_text("module blah; endmodule")
            Path(tmp, "6_final.gds").write_bytes(b"\x00" * 100)
            builder = InvestigationContextBuilder(tmp)
            context = builder.build()
            assert "design.v" not in json.dumps(context)
            assert "6_final.gds" not in json.dumps(context)


class TestPromptTemplate:

    def test_system_prompt_has_required_rules(self):
        prompt = get_system_prompt()
        assert "Never claim" in prompt
        assert "Never override" in prompt
        assert "hypotheses" in prompt
        assert "Return JSON only" in prompt

    def test_system_prompt_contains_schema(self):
        prompt = get_system_prompt()
        assert "investigation_status" in prompt
        assert "possible_causes" in prompt
        assert "disclaimer" in prompt


class TestSchema:

    def test_valid_payload(self):
        raw = json.dumps({
            "investigation_status": "EXPERIMENTAL",
            "summary": "Test summary",
            "facts": [{"observation": "WNS is negative", "source": "metrics.csv", "evidence": "-0.5"}],
            "possible_causes": [{"cause": "Timing violation", "confidence": "MEDIUM", "reasoning": "WNS < 0", "supporting_evidence": ["WNS=-0.5"]}],
            "recommended_next_steps": ["Check timing constraints"],
            "missing_information": ["Hold timing data"],
            "disclaimer": "AI-generated.",
        })
        result = InvestigationSchema.validate(raw)
        assert result.valid
        assert len(result.errors) == 0

    def test_empty_response(self):
        result = InvestigationSchema.validate("")
        assert not result.valid
        assert "Empty response" in str(result.errors)

    def test_invalid_json(self):
        result = InvestigationSchema.validate("{bad json}")
        assert not result.valid
        assert "Invalid JSON" in str(result.errors)

    def test_missing_fields(self):
        raw = json.dumps({"investigation_status": "EXPERIMENTAL"})
        result = InvestigationSchema.validate(raw)
        assert not result.valid
        assert any("summary" in e for e in result.errors)

    def test_extract_json_from_markdown_fence(self):
        raw = 'Here is the result:\n```json\n{"investigation_status": "EXPERIMENTAL", "summary": "test", "facts": [], "possible_causes": [], "recommended_next_steps": [], "missing_information": [], "disclaimer": "x"}\n```\nEnd'
        result = InvestigationSchema.validate(raw)
        assert result.valid

    def test_extract_json_with_leading_text(self):
        raw = 'Some text before\n{"investigation_status": "EXPERIMENTAL", "summary": "test", "facts": [], "possible_causes": [], "recommended_next_steps": [], "missing_information": [], "disclaimer": "x"}\ntrailing'
        result = InvestigationSchema.validate(raw)
        assert result.valid

    def test_no_json_object(self):
        result = InvestigationSchema.validate("Just some text with no JSON")
        assert not result.valid
        assert "No JSON object" in str(result.errors)

    def test_build_failed(self):
        failed = InvestigationSchema.build_failed("API timeout")
        assert failed["investigation_status"] == "FAILED"
        assert "timeout" in failed["summary"]

    def test_facts_max_warning(self):
        facts = [{"observation": f"fact_{i}", "source": "test"} for i in range(25)]
        raw = json.dumps({
            "investigation_status": "EXPERIMENTAL",
            "summary": "test",
            "facts": facts,
            "possible_causes": [],
            "recommended_next_steps": [],
            "missing_information": [],
            "disclaimer": "test",
        })
        result = InvestigationSchema.validate(raw)
        assert result.valid
        assert len(result.warnings) > 0


class TestBharatCodeProvider:

    def test_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = BharatCodeProvider()
            assert not provider.is_available()
            resp = provider.investigate("prompt", "context")
            assert not resp.success
            assert "API key" in (resp.error or "")

    def test_with_api_key_available(self):
        with patch.dict(os.environ, {"BHARATCODE_API_KEY": "test-key-123"}):
            provider = BharatCodeProvider()
            assert provider.is_available()

    def test_timeout_handling(self):
        with patch.dict(os.environ, {"BHARATCODE_API_KEY": "test-key"}):
            provider = BharatCodeProvider(timeout_sec=1, retry_attempts=1)
            resp = provider.investigate("prompt", "context")
            assert not resp.success  # will timeout since no real server

    def test_401_handling(self):
        with patch.dict(os.environ, {"BHARATCODE_API_KEY": "bad-key"}):
            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.post.return_value.status_code = 401
                mock_client.return_value.__enter__.return_value = mock_instance
                provider = BharatCodeProvider()
                resp = provider.investigate("prompt", "context")
                assert not resp.success
                assert "401" in (resp.error or "")


class TestInvestigationLayer:

    def test_config_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual_config = Path(__file__).parent.parent.parent / "configs" / "ai_investigation.yaml"
            orig = None
            if actual_config.exists():
                orig = actual_config.read_text()
            actual_config.parent.mkdir(parents=True, exist_ok=True)
            actual_config.write_text("enabled: true\nprovider:\n  name: test")
            try:
                layer = InvestigationLayer(run_dir=tmp, run_id="test_001")
                assert layer.config["enabled"] is True
                assert layer.config["provider"]["name"] == "test"
            finally:
                if orig is not None:
                    actual_config.write_text(orig)
                elif actual_config.exists():
                    actual_config.unlink()

    def test_auto_investigate_disabled_when_not_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {}, clear=True):
                layer = InvestigationLayer(run_dir=tmp, run_id="test_002")
                assert not layer.should_auto_investigate()

    def test_auto_investigate_skips_high_confidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"BHARATCODE_API_KEY": "test-key"}):
                layer = InvestigationLayer(run_dir=tmp, run_id="test_003")
                assert not layer.should_auto_investigate(root_cause_confidence=0.85)
                assert layer.should_auto_investigate(root_cause_confidence=0.30)

    def test_investigate_no_api_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {}, clear=True):
                layer = InvestigationLayer(run_dir=tmp, run_id="test_004")
                result = layer.investigate()
                assert result.status == "UNAVAILABLE"

    def test_save_investigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"BHARATCODE_API_KEY": "test-key"}):
                layer = InvestigationLayer(run_dir=tmp, run_id="test_005")
                result = InvestigationResult(
                    status="EXPERIMENTAL",
                    payload={"summary": "test", "facts": [], "possible_causes": [], "recommended_next_steps": [], "missing_information": [], "disclaimer": ""},
                    provider="bharatcode",
                    model="test-model",
                )
                path = layer.save_investigation(result)
                assert path.exists()
                data = json.loads(path.read_text())
                assert data["status"] == "EXPERIMENTAL"
                assert data["investigation"]["summary"] == "test"


class TestInvestigationIntegration:

    def test_context_to_api_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "drc_lvs_summary.json").write_text(json.dumps({
                "drc": {"total_violations": 4, "is_clean": False},
                "lvs": {"result": "FAIL", "is_clean": False},
            }))
            builder = InvestigationContextBuilder(tmp)
            context_dict, context_str = builder.build_for_api()
            assert "DRC" in context_str
            assert "LVS" in context_str
            assert context_dict["run_id"] == Path(tmp).name
