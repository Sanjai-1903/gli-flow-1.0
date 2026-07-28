import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

SETTINGS_FILE = Path.home() / ".gli-flow" / "telemetry_settings.json"

class TelemetryMode:
    FULL = "full"
    ATLAS = "atlas"
    LOCAL = "local"
    DISABLED = "disabled"

class TelemetrySettings:
    def __init__(self):
        self.settings = self._load()

    def _load(self) -> Dict[str, Any]:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save(self):
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    @property
    def mode(self) -> str:
        return self.settings.get("telemetry_mode", TelemetryMode.LOCAL)

    @mode.setter
    def mode(self, value: str):
        if value not in [TelemetryMode.FULL, TelemetryMode.ATLAS, TelemetryMode.LOCAL, TelemetryMode.DISABLED]:
            raise ValueError(f"Invalid telemetry mode: {value}")
        self.settings["telemetry_mode"] = value

    @property
    def consent_given(self) -> bool:
        return self.settings.get("consent_given", False)

    @consent_given.setter
    def consent_given(self, value: bool):
        self.settings["consent_given"] = value
        if value:
            self.settings["consent_timestamp"] = datetime.now(timezone.utc).isoformat()

    @property
    def version(self) -> str:
        return self.settings.get("version", "1.0")

    @version.setter
    def version(self, value: str):
        self.settings["version"] = value

    def is_wizard_required(self) -> bool:
        # Wizard is required if consent is not given and mode is not explicitly set to DISABLED/LOCAL by enterprise override
        if self.settings.get("telemetry_mode") == TelemetryMode.DISABLED:
            return False
        return not self.consent_given

def get_telemetry_settings() -> TelemetrySettings:
    return TelemetrySettings()
