"""Tests for InvestigationAvailabilityService - single source of truth."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import httpx

from gli_flow.investigation.availability import (
    InvestigationAvailabilityService,
    AvailabilityResult,
    ENV_KEY_NAME,
    PLACEHOLDER_KEYS,
    _is_placeholder,
)


class TestPlaceholderDetection:

    def test_none_is_placeholder(self):
        assert _is_placeholder(None)

    def test_empty_string_is_placeholder(self):
        assert _is_placeholder("")

    def test_whitespace_only_is_placeholder(self):
        assert _is_placeholder("   ")

    @pytest.mark.parametrize("key", ["your-key-here", "Your-Key-Here", "YOUR-KEY-HERE"])
    def test_your_key_here_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["placeholder", "PLACEHOLDER", "Placeholder"])
    def test_placeholder_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["changeme", "ChangeMe", "CHANGEME"])
    def test_changeme_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["test", "TEST", "Test"])
    def test_test_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["dummy", "DUMMY", "Dummy"])
    def test_dummy_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["sample", "SAMPLE", "Sample"])
    def test_sample_variants(self, key):
        assert _is_placeholder(key)

    @pytest.mark.parametrize("key", ["sk-real-key-12345", "valid-key-abcdef", "real-api-key-12345"])
    def test_valid_keys_not_placeholder(self, key):
        assert not _is_placeholder(key)

    def test_placeholder_set_contains_all_required(self):
        expected = {"your-key-here", "placeholder", "changeme", "test", "dummy", "sample", ""}
        assert PLACEHOLDER_KEYS == expected


class TestMissingKey:

    def test_no_env_var_returns_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert result.status == "INVALID_CONFIGURATION"
            assert not result.api_key_present
            assert "Missing" in result.reason

    def test_empty_env_var_returns_unavailable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: ""}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert not result.api_key_present

    def test_whitespace_env_var_returns_unavailable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "   "}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert not result.api_key_present


class TestPlaceholderKey:

    @pytest.mark.parametrize("key", ["your-key-here", "placeholder", "changeme", "test", "dummy", "sample"])
    def test_placeholder_key_rejected(self, key):
        with patch.dict(os.environ, {ENV_KEY_NAME: key}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert result.status == "INVALID_CONFIGURATION"
            assert result.api_key_present
            assert not result.api_key_valid
            assert "placeholder" in result.reason.lower()

    def test_placeholder_key_case_insensitive(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "YOUR-KEY-HERE"}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert not result.api_key_valid


class TestInvalidKey:

    def test_short_key_rejected(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "abc"}, clear=True):
            service = InvestigationAvailabilityService()
            result = service.check_availability()
            assert not result.is_ready
            assert result.api_key_present
            assert not result.api_key_valid
            assert "too short" in result.reason.lower()


class TestModelNotConfigured:

    def test_empty_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "ai_investigation.yaml"
            config_path.write_text("enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com\n  model: ''")
            with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
                service = InvestigationAvailabilityService(config_path=str(config_path))
                result = service.check_availability()
                assert not result.is_ready
                assert result.api_key_present
                assert result.api_key_valid
                assert not result.model_configured
                assert result.status == "MISCONFIGURED"

    def test_missing_model_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "ai_investigation.yaml"
            config_path.write_text("enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com")
            with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
                service = InvestigationAvailabilityService(config_path=str(config_path))
                result = service.check_availability()
                assert not result.is_ready
                assert result.api_key_present
                assert result.api_key_valid
                assert not result.model_configured


class TestProviderTimeout:

    def test_provider_timeout_returns_unavailable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_instance.get.side_effect = httpx.TimeoutException("timeout")
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert not result.is_ready
                    assert result.api_key_present
                    assert result.api_key_valid
                    assert result.model_configured
                    assert not result.provider_reachable
                    assert result.status == "UNAVAILABLE"


class TestProvider401:

    def test_provider_401_treated_as_reachable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 401
                    mock_instance.get.return_value = mock_response
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert result.is_ready
                    assert result.provider_reachable


class TestProvider429:

    def test_provider_429_treated_as_reachable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 429
                    mock_instance.get.return_value = mock_response
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert result.is_ready
                    assert result.provider_reachable


class TestProvider500:

    def test_provider_500_treated_as_reachable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 500
                    mock_instance.get.return_value = mock_response
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert result.is_ready
                    assert result.provider_reachable


class TestNetworkFailure:

    def test_network_error_returns_unavailable(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_instance.get.side_effect = httpx.RequestError("network error")
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert not result.is_ready
                    assert result.api_key_present
                    assert result.api_key_valid
                    assert result.model_configured
                    assert not result.provider_reachable
                    assert "not reachable" in result.reason.lower()


class TestReadyState:

    def test_all_checks_pass_returns_ready(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_instance.get.return_value = mock_response
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    assert result.is_ready
                    assert result.status == "READY"
                    assert result.enabled
                    assert result.api_key_present
                    assert result.api_key_valid
                    assert result.model_configured
                    assert result.provider_reachable
                    assert result.provider == "bharatcode"


class TestDisabledInvestigation:

    def test_disabled_in_config_returns_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "ai_investigation.yaml"
            config_path.write_text("enabled: false")
            with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
                service = InvestigationAvailabilityService(config_path=str(config_path))
                result = service.check_availability()
                assert not result.is_ready
                assert result.status == "UNAVAILABLE"
                assert not result.enabled


class TestAvailabilityResultDataclass:

    def test_defaults(self):
        result = AvailabilityResult()
        assert result.status == "UNAVAILABLE"
        assert not result.is_ready

    def test_ready_status(self):
        result = AvailabilityResult(status="READY")
        assert result.is_ready


class TestServiceMethod:

    def test_is_placeholder_key_static(self):
        assert InvestigationAvailabilityService.is_placeholder_key("test")
        assert InvestigationAvailabilityService.is_placeholder_key("")
        assert InvestigationAvailabilityService.is_placeholder_key(None)
        assert not InvestigationAvailabilityService.is_placeholder_key("sk-real-key")


class TestHealthEndpointContract:
    """Verify the health endpoint contract matches what frontend expects."""

    def test_health_response_has_all_fields(self):
        with patch.dict(os.environ, {ENV_KEY_NAME: "sk-real-key-12345"}, clear=True):
            with tempfile.TemporaryDirectory() as tmp:
                config_path = Path(tmp) / "ai_investigation.yaml"
                config_path.write_text(
                    "enabled: true\nprovider:\n  name: bharatcode\n  endpoint: https://api.example.com/v1/chat/completions\n  model: test-model"
                )
                with patch("httpx.Client") as mock_client:
                    mock_instance = MagicMock()
                    mock_instance.get.return_value.status_code = 200
                    mock_client.return_value.__enter__.return_value = mock_instance
                    service = InvestigationAvailabilityService(config_path=str(config_path))
                    result = service.check_availability()
                    response = {
                        "enabled": result.enabled,
                        "provider": result.provider,
                        "api_key_present": result.api_key_present,
                        "api_key_valid": result.api_key_valid,
                        "model_configured": result.model_configured,
                        "provider_reachable": result.provider_reachable,
                        "status": result.status,
                        "reason": result.reason,
                        "fix": result.fix,
                    }
                    assert "enabled" in response
                    assert "provider" in response
                    assert "api_key_present" in response
                    assert "api_key_valid" in response
                    assert "model_configured" in response
                    assert "provider_reachable" in response
                    assert "status" in response
                    assert "reason" in response
                    assert "fix" in response
