"""BharatCode API provider for LLM investigation.

Reads BHARATCODE_API_KEY from environment.
Never exposes key to frontend, dashboard, browser, or telemetry.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

try:
    import httpx
except ImportError:
    httpx = None  # Deferred — only needed for AI investigation

logger = logging.getLogger(__name__)

ENV_KEY_NAME = "BHARATCODE_API_KEY"
DEFAULT_ENDPOINT = "https://api.bharatcode.ai/v1/chat/completions"
DEFAULT_MODEL = "bharatcode-investigation-v1"

PLACEHOLDER_KEYS = {"your-key-here", "placeholder", "changeme", "test", "dummy", "sample", ""}


@dataclass
class ProviderResponse:
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    latency_sec: float = 0.0
    retries: int = 0


class BharatCodeProvider:

    PLACEHOLDER_KEYS = {"your-key-here", "placeholder", "changeme", "test", "dummy", "sample", ""}

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        timeout_sec: int = 60,
        retry_attempts: int = 2,
        retry_delay_sec: int = 5,
    ):
        self.endpoint = endpoint
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_sec = timeout_sec
        self.retry_attempts = retry_attempts
        self.retry_delay_sec = retry_delay_sec
        self._api_key: Optional[str] = None

    def _get_api_key(self) -> Optional[str]:
        if self._api_key is None:
            self._api_key = os.environ.get(ENV_KEY_NAME)
        return self._api_key

    @staticmethod
    def _is_placeholder_key(key: Optional[str]) -> bool:
        if key is None:
            return True
        return key.strip().lower() in PLACEHOLDER_KEYS

    def is_available(self) -> bool:
        key = self._get_api_key()
        if self._is_placeholder_key(key):
            return False
        return key is not None and len(key) > 0

    def preflight_check(self) -> Optional[str]:
        key = self._get_api_key()
        if key is None or len(key) == 0:
            return f"{ENV_KEY_NAME} is not set. Investigation unavailable."
        if self._is_placeholder_key(key):
            return f"Invalid API key configured. {ENV_KEY_NAME} contains a placeholder value."
        if not self.endpoint or not self.endpoint.startswith("http"):
            return f"Provider endpoint is not configured: {self.endpoint}"
        if not self.model:
            return "Provider model is not configured."
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(self.endpoint.replace("/chat/completions", "/models"))
                if resp.status_code == 401 or resp.status_code == 403:
                    return None
        except (httpx.TimeoutException, httpx.RequestError, Exception):
            pass
        return None

    def investigate(self, system_prompt: str, context: str) -> ProviderResponse:
        api_key = self._get_api_key()
        if not api_key:
            return ProviderResponse(
                success=False,
                error=f"API key not set. Set {ENV_KEY_NAME} environment variable.",
            )
        if self._is_placeholder_key(api_key):
            return ProviderResponse(
                success=False,
                error=f"Invalid API key configured. {ENV_KEY_NAME} contains a placeholder value.",
            )

        last_error = None
        attempts = 0
        start = time.monotonic()

        for attempt in range(1 + self.retry_attempts):
            attempts += 1
            try:
                with httpx.Client(timeout=self.timeout_sec) as client:
                    resp = client.post(
                        self.endpoint,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": context},
                            ],
                            "max_tokens": self.max_tokens,
                            "temperature": self.temperature,
                        },
                    )
                    if resp.status_code == 401:
                        return ProviderResponse(
                            success=False,
                            error="Invalid API key (401). Check BHARATCODE_API_KEY.",
                        )
                    if resp.status_code == 429:
                        last_error = f"Rate limited (429) on attempt {attempt}"
                        if attempt <= self.retry_attempts:
                            time.sleep(self.retry_delay_sec)
                            continue
                        break
                    if resp.status_code >= 500:
                        last_error = f"Server error ({resp.status_code}) on attempt {attempt}"
                        if attempt <= self.retry_attempts:
                            time.sleep(self.retry_delay_sec)
                            continue
                        break
                    if resp.status_code != 200:
                        last_error = f"API error ({resp.status_code}): {resp.text[:500]}"
                        break

                    data = resp.json()
                    msg = data.get("choices", [{}])[0].get("message", {})
                    finish_reason = data.get("choices", [{}])[0].get("finish_reason", "unknown")
                    content = msg.get("content") or msg.get("reasoning") or ""
                    if not content.strip():
                        last_error = f"API returned empty message: finish_reason={finish_reason}"
                        logger.warning(f"BharatCode empty response. finish_reason={finish_reason}, raw={resp.text[:500]}")
                        break
                    if finish_reason == "length":
                        logger.warning(f"BharatCode response truncated (finish_reason=length). content_len={len(content)}")
                    if msg.get("content") is None and msg.get("reasoning"):
                        logger.info(f"Using reasoning field as content (model: {data.get('model', 'unknown')})")
                    latency = round(time.monotonic() - start, 2)
                    return ProviderResponse(
                        success=True,
                        content=content,
                        latency_sec=latency,
                        retries=attempt - 1,
                    )

            except httpx.TimeoutException:
                last_error = f"Timeout after {self.timeout_sec}s on attempt {attempt}"
                if attempt <= self.retry_attempts:
                    time.sleep(self.retry_delay_sec)
                    continue
                break
            except httpx.RequestError as e:
                last_error = f"Connection error on attempt {attempt}: {e}"
                if attempt <= self.retry_attempts:
                    time.sleep(self.retry_delay_sec)
                    continue
                break
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                break

        latency = round(time.monotonic() - start, 2)
        return ProviderResponse(
            success=False,
            error=last_error or "Unknown error",
            latency_sec=latency,
            retries=attempts - 1,
        )
