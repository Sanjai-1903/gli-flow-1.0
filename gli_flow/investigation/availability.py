"""Single source of truth for AI investigation availability.

All UI and backend paths must use this service to determine:
- API key configured?
- API key valid?
- Provider reachable?
- Model configured?
- Investigation enabled?
- Investigation supported for this run?
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

try:
    import httpx
except ImportError:
    httpx = None  # Provides type-checkable fallback

logger = logging.getLogger(__name__)

ENV_KEY_NAME = "BHARATCODE_API_KEY"
CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "ai_investigation.yaml"

PLACEHOLDER_KEYS = {
    "your-key-here",
    "placeholder",
    "changeme",
    "test",
    "dummy",
    "sample",
    "",
}


def _is_placeholder(key: Optional[str]) -> bool:
    if key is None:
        return True
    return key.strip().lower() in PLACEHOLDER_KEYS


@dataclass
class AvailabilityResult:
    enabled: bool = True
    provider: str = "bharatcode"
    api_key_present: bool = False
    api_key_valid: bool = False
    model_configured: bool = False
    provider_reachable: bool = False
    status: str = "UNAVAILABLE"
    reason: str = ""
    fix: str = ""

    @property
    def is_ready(self) -> bool:
        return self.status == "READY"


class InvestigationAvailabilityService:
    """Single source of truth for AI investigation availability.

    Usage:
        service = InvestigationAvailabilityService()
        result = service.check_availability()
        if result.is_ready:
            # Show "Run AI Investigation" button
        else:
            # Show reason and fix
    """

    def __init__(self, config_path: Optional[str] = None):
        self._config = self._load_config(config_path)
        self._api_key: Optional[str] = None

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        path = Path(config_path) if config_path else CONFIG_PATH
        default = {
            "enabled": True,
            "provider": {
                "name": "bharatcode",
                "endpoint": "https://api.bharatcode.ai/v1/chat/completions",
                "model": "bharatcode-investigation-v1",
            },
        }
        if path.exists():
            try:
                with open(path) as f:
                    loaded = yaml.safe_load(f)
                    if loaded and isinstance(loaded, dict):
                        default.update(loaded)
            except Exception as e:
                logger.warning("Failed to load config from %s: %s", path, e)
        return default

    def _get_api_key(self) -> Optional[str]:
        if self._api_key is None:
            self._api_key = os.environ.get(ENV_KEY_NAME)
        return self._api_key

    @staticmethod
    def is_placeholder_key(key: Optional[str]) -> bool:
        return _is_placeholder(key)

    def check_availability(self) -> AvailabilityResult:
        """Check all availability criteria and return detailed result."""

        enabled = self._config.get("enabled", True)
        if not enabled:
            return AvailabilityResult(
                enabled=False,
                status="UNAVAILABLE",
                reason="AI investigation is disabled in configuration",
                fix='Enable investigation in configs/ai_investigation.yaml (set enabled: true)',
            )

        api_key = self._get_api_key()
        if not api_key or not api_key.strip():
            return AvailabilityResult(
                api_key_present=False,
                status="INVALID_CONFIGURATION",
                reason="Missing BharatCode API key",
                fix=f"Set {ENV_KEY_NAME} in .env",
            )

        api_key_present = True

        if self.is_placeholder_key(api_key):
            return AvailabilityResult(
                api_key_present=True,
                api_key_valid=False,
                status="INVALID_CONFIGURATION",
                reason="BharatCode API key is a placeholder value",
                fix=f"Replace the placeholder value of {ENV_KEY_NAME} with a real API key",
            )

        if len(api_key.strip()) < 8:
            return AvailabilityResult(
                api_key_present=True,
                api_key_valid=False,
                status="INVALID_CONFIGURATION",
                reason="BharatCode API key format appears invalid (too short)",
                fix="Ensure BHARATCODE_API_KEY is a valid API key (minimum 8 characters)",
            )

        api_key_valid = True

        provider_config = self._config.get("provider", {})
        model = provider_config.get("model", "")
        if not model:
            return AvailabilityResult(
                api_key_present=True,
                api_key_valid=True,
                model_configured=False,
                status="MISCONFIGURED",
                reason="No AI model configured",
                fix="Set a model in configs/ai_investigation.yaml under provider.model",
            )

        model_configured = True

        endpoint = provider_config.get("endpoint", "")
        if not endpoint or not endpoint.startswith("http"):
            return AvailabilityResult(
                api_key_present=True,
                api_key_valid=True,
                model_configured=True,
                provider_reachable=False,
                status="MISCONFIGURED",
                reason="Provider endpoint not configured",
                fix="Set provider endpoint in configs/ai_investigation.yaml",
            )

        reachable = self._check_provider_reachable(endpoint)
        if not reachable:
            return AvailabilityResult(
                api_key_present=True,
                api_key_valid=True,
                model_configured=True,
                provider_reachable=False,
                status="UNAVAILABLE",
                reason="BharatCode provider is not reachable",
                fix="Check network connectivity and provider endpoint URL",
            )

        return AvailabilityResult(
            enabled=True,
            provider=provider_config.get("name", "bharatcode"),
            api_key_present=True,
            api_key_valid=True,
            model_configured=True,
            provider_reachable=True,
            status="READY",
        )

    def _check_provider_reachable(self, endpoint: str) -> bool:
        try:
            models_endpoint = endpoint.replace("/chat/completions", "/models")
            with httpx.Client(timeout=10) as client:
                client.get(models_endpoint)
                return True
        except (httpx.TimeoutException, httpx.RequestError, Exception) as e:
            logger.warning("Provider not reachable at %s: %s", endpoint, e)
            return False
