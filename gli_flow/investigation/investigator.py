"""Investigation Layer orchestrator.

Tier 2 (Experimental) — activated when Tier 1 (Trusted) deterministic
systems cannot confidently explain a failure.

Hardened with:
- Investigation immutability (successful results never overwritten by failures)
- Investigation history (investigations/ directory with numbered snapshots)
- Backup protection (investigation.backup.json before replacement)
- Pre-flight checks (API key validation, provider reachability)
- Failed attempt tracking
"""

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from gli_flow.investigation.context_builder import InvestigationContextBuilder
from gli_flow.investigation.prompt_template import get_system_prompt
from gli_flow.investigation.providers.bharatcode import BharatCodeProvider
from gli_flow.investigation.schema import InvestigationSchema
from gli_flow.investigation.availability import InvestigationAvailabilityService

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent.parent / "configs" / "ai_investigation.yaml"

SUCCESS_STATUSES = {"EXPERIMENTAL"}
FAILURE_STATUSES = {"FAILED", "SKIPPED", "UNAVAILABLE"}


@dataclass
class InvestigationResult:
    status: str
    payload: Optional[dict] = None
    error: Optional[str] = None
    provider: str = ""
    model: str = ""
    latency_sec: float = 0.0

    def is_success(self) -> bool:
        return self.status in SUCCESS_STATUSES


@dataclass
class FailedAttempt:
    status: str
    error: str
    timestamp: str
    provider: str = ""
    model: str = ""
    latency_sec: float = 0.0


class InvestigationLayer:

    MAX_HISTORY = 10
    INVESTIGATIONS_DIR = "investigations"
    LATEST_LINK = "latest.json"
    BACKUP_FILE = "investigation.backup.json"
    MAIN_FILE = "investigation.json"
    FAILED_ATTEMPTS_FILE = "failed_attempts.json"

    def __init__(self, run_dir: str, run_id: str):
        self.run_dir = Path(run_dir)
        self.run_id = run_id
        self.config = self._load_config()
        self.provider = self._create_provider()
        self._availability_service = InvestigationAvailabilityService()

    def _load_config(self) -> dict:
        default = {
            "enabled": True,
            "auto_trigger_unknown_failures": True,
            "confidence_threshold": 0.60,
            "provider": {
                "name": "bharatcode",
                "endpoint": "https://api.bharatcode.ai/v1/chat/completions",
                "model": "bharatcode-investigation-v1",
                "max_tokens": 2048,
                "temperature": 0.1,
                "timeout_sec": 60,
                "retry_attempts": 2,
                "retry_delay_sec": 5,
            },
        }
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH) as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        default.update(loaded)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        return default

    def _create_provider(self) -> BharatCodeProvider:
        pcfg = self.config.get("provider", {})
        return BharatCodeProvider(
            endpoint=pcfg.get("endpoint", "https://api.bharatcode.ai/v1/chat/completions"),
            model=pcfg.get("model", "bharatcode-investigation-v1"),
            max_tokens=pcfg.get("max_tokens", 2048),
            temperature=pcfg.get("temperature", 0.1),
            timeout_sec=pcfg.get("timeout_sec", 60),
            retry_attempts=pcfg.get("retry_attempts", 2),
            retry_delay_sec=pcfg.get("retry_delay_sec", 5),
        )

    def should_auto_investigate(self, root_cause_confidence: Optional[float] = None) -> bool:
        if not self.config.get("enabled", True):
            return False
        if not self.provider.is_available():
            return False
        if not self.config.get("auto_trigger_unknown_failures", True):
            return False
        threshold = self.config.get("confidence_threshold", 0.60)
        if root_cause_confidence is not None and root_cause_confidence >= threshold:
            return False
        return True

    def is_available(self) -> bool:
        return self.config.get("enabled", True) and self.provider.is_available()

    def preflight_check(self) -> Optional[str]:
        if not self.config.get("enabled", True):
            return "AI investigation is disabled in configs/ai_investigation.yaml"
        return self.provider.preflight_check()

    def check_availability(self):
        """Delegate to InvestigationAvailabilityService for detailed availability."""
        return self._availability_service.check_availability()

    def _investigations_dir(self) -> Path:
        return self.run_dir / self.INVESTIGATIONS_DIR

    def _main_path(self) -> Path:
        return self.run_dir / self.MAIN_FILE

    def _backup_path(self) -> Path:
        return self.run_dir / self.BACKUP_FILE

    def _latest_link_path(self) -> Path:
        return self._investigations_dir() / self.LATEST_LINK

    def _failed_attempts_path(self) -> Path:
        return self.run_dir / self.FAILED_ATTEMPTS_FILE

    def _read_json(self, path: Path) -> Optional[dict]:
        try:
            if path.exists():
                return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to read {path}: {e}")
        return None

    def _write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    def has_successful_investigation(self) -> bool:
        main = self._read_json(self._main_path())
        if main and main.get("status") in SUCCESS_STATUSES:
            return True
        inv_dir = self._investigations_dir()
        if inv_dir.exists():
            latest = self._read_json(self._latest_link_path())
            if latest and latest.get("status") in SUCCESS_STATUSES:
                return True
        return False

    def get_successful_investigation(self) -> Optional[dict]:
        main = self._read_json(self._main_path())
        if main and main.get("status") in SUCCESS_STATUSES:
            return main
        inv_dir = self._investigations_dir()
        if inv_dir.exists():
            latest = self._read_json(self._latest_link_path())
            if latest and latest.get("status") in SUCCESS_STATUSES:
                return latest
        return None

    def get_failed_attempts(self) -> list[dict]:
        data = self._read_json(self._failed_attempts_path())
        if data and isinstance(data.get("attempts"), list):
            return data["attempts"]
        return []

    def get_investigation_history(self) -> list[dict]:
        history = []
        inv_dir = self._investigations_dir()
        if not inv_dir.exists():
            return history
        try:
            files = sorted(inv_dir.glob("investigation_*.json"))
            for f in files:
                data = self._read_json(f)
                if data:
                    data["_file"] = f.name
                    history.append(data)
        except OSError:
            pass
        return history

    def _backup_existing(self) -> bool:
        main = self._main_path()
        if main.exists():
            try:
                shutil.copy2(str(main), str(self._backup_path()))
                logger.info(f"Backed up {main} to {self._backup_path()}")
                return True
            except OSError as e:
                logger.warning(f"Failed to backup investigation: {e}")
        return False

    def _save_to_history(self, result_data: dict) -> Path:
        inv_dir = self._investigations_dir()
        inv_dir.mkdir(parents=True, exist_ok=True)

        existing = sorted(inv_dir.glob("investigation_*.json"))
        next_num = 1
        if existing:
            last_name = existing[-1].stem
            try:
                last_num = int(last_name.split("_")[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = len(existing) + 1

        history_path = inv_dir / f"investigation_{next_num:04d}.json"
        self._write_json(history_path, result_data)

        self._write_json(self._latest_link_path(), result_data)

        self._prune_history(inv_dir)
        return history_path

    def _prune_history(self, inv_dir: Path) -> None:
        try:
            files = sorted(inv_dir.glob("investigation_*.json"))
            while len(files) > self.MAX_HISTORY:
                oldest = files.pop(0)
                if oldest.name != self.LATEST_LINK:
                    oldest.unlink()
                    logger.info(f"Pruned old investigation: {oldest}")
        except OSError:
            pass

    def _record_failed_attempt(self, result: InvestigationResult) -> None:
        attempt = {
            "status": result.status,
            "error": result.error or "Unknown error",
            "timestamp": datetime.now().isoformat(),
            "provider": result.provider,
            "model": result.model,
            "latency_sec": result.latency_sec,
        }
        path = self._failed_attempts_path()
        existing = self._read_json(path) or {"attempts": []}
        existing["attempts"].append(attempt)
        attempts = existing["attempts"]
        while len(attempts) > self.MAX_HISTORY:
            attempts.pop(0)
        self._write_json(path, existing)

    def investigate(self) -> InvestigationResult:
        if not self.config.get("enabled", True):
            return InvestigationResult(
                status="SKIPPED",
                error="AI investigation is disabled in configs/ai_investigation.yaml",
            )

        if not self.provider.is_available():
            return InvestigationResult(
                status="UNAVAILABLE",
                error="BHARATCODE_API_KEY not set or contains a placeholder value. Investigation unavailable.",
            )

        context_builder = InvestigationContextBuilder(str(self.run_dir))
        context_dict, context_str = context_builder.build_for_api()

        system_prompt = get_system_prompt()

        provider_resp = self.provider.investigate(system_prompt, context_str)
        if not provider_resp.success:
            return InvestigationResult(
                status="FAILED",
                error=provider_resp.error or "Provider returned no response",
                provider=self.config.get("provider", {}).get("name", "bharatcode"),
                model=self.config.get("provider", {}).get("model", ""),
                latency_sec=provider_resp.latency_sec,
            )

        validation = InvestigationSchema.validate(provider_resp.content or "")
        if not validation.valid:
            failed_payload = InvestigationSchema.build_failed(
                "; ".join(validation.errors)
            )
            return InvestigationResult(
                status="FAILED",
                payload=failed_payload,
                error="; ".join(validation.errors),
                provider=self.config.get("provider", {}).get("name", "bharatcode"),
                model=self.config.get("provider", {}).get("model", ""),
                latency_sec=provider_resp.latency_sec,
            )

        payload = validation.payload or {}
        payload["provider"] = self.config.get("provider", {}).get("name", "bharatcode")
        payload["model"] = self.config.get("provider", {}).get("model", "")
        payload["generated_at"] = datetime.now().isoformat()
        payload["latency_sec"] = provider_resp.latency_sec

        return InvestigationResult(
            status="EXPERIMENTAL",
            payload=payload,
            provider=self.config.get("provider", {}).get("name", "bharatcode"),
            model=self.config.get("provider", {}).get("model", ""),
            latency_sec=provider_resp.latency_sec,
        )

    def save_investigation(self, result: InvestigationResult) -> Path:
        if result.is_success():
            return self._save_successful_investigation(result)
        else:
            return self._save_failed_investigation(result)

    def _build_result_data(self, result: InvestigationResult) -> dict:
        data = {
            "run_id": self.run_id,
            "timestamp": datetime.now().isoformat(),
            "provider": result.provider,
            "model": result.model,
            "status": result.status,
            "latency_sec": result.latency_sec,
        }
        if result.payload:
            data["investigation"] = result.payload
        if result.error:
            data["error"] = result.error
        return data

    def _save_successful_investigation(self, result: InvestigationResult) -> Path:
        result_data = self._build_result_data(result)

        self._backup_existing()

        self._write_json(self._main_path(), result_data)

        self._save_to_history(result_data)

        logger.info(f"Saved successful investigation ({result.status}) for {self.run_id}")
        return self._main_path()

    def _save_failed_investigation(self, result: InvestigationResult) -> Path:
        self._record_failed_attempt(result)

        has_existing = self.has_successful_investigation()

        if has_existing:
            logger.info(
                f"Preserving existing successful investigation for {self.run_id} "
                f"(failed attempt recorded: {result.error})"
            )
            return self._main_path()

        result_data = self._build_result_data(result)
        self._write_json(self._main_path(), result_data)

        self._save_to_history(result_data)

        logger.info(f"Saved failed investigation ({result.status}) for {self.run_id}")
        return self._main_path()

    def restore_from_backup(self) -> bool:
        backup = self._backup_path()
        main = self._main_path()
        if not backup.exists():
            logger.warning(f"No backup found at {backup}")
            return False
        try:
            backup_data = self._read_json(backup)
            if backup_data and backup_data.get("status") in SUCCESS_STATUSES:
                shutil.copy2(str(backup), str(main))
                self._save_to_history(backup_data)
                logger.info(f"Restored successful investigation from backup for {self.run_id}")
                return True
            else:
                logger.warning(f"Backup at {backup} does not contain a successful investigation")
                return False
        except OSError as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    def migrate_failed_investigations(self) -> bool:
        main = self._read_json(self._main_path())
        if not main:
            return False
        if main.get("status") not in FAILURE_STATUSES:
            return False
        backup = self._read_json(self._backup_path())
        if backup and backup.get("status") in SUCCESS_STATUSES:
            logger.info(f"Migration: restoring successful investigation from backup for {self.run_id}")
            return self.restore_from_backup()
        inv_dir = self._investigations_dir()
        if inv_dir.exists():
            history = self.get_investigation_history()
            for entry in history:
                if entry.get("status") in SUCCESS_STATUSES:
                    logger.info(f"Migration: restoring successful investigation from history for {self.run_id}")
                    self._write_json(self._main_path(), entry)
                    return True
        return False
